"""
LLM-Enhanced Feedback Parsing — Use Claude API for natural language understanding.

Upgrades the basic feedback parser with LLM capabilities:
- Better intent extraction from complex feedback
- Handling ambiguous or nuanced feedback
- Multi-step feedback parsing
- Confidence scoring
"""

from typing import Optional, Dict
from src.feedback import FeedbackIntent, AdjustmentType
import os


class LLMFeedbackParser:
    """
    Enhanced feedback parser using Claude LLM.

    Provides better understanding of complex, natural feedback like:
    - "That song was nice but a bit too energetic for focus work"
    - "I liked the mood, but I want something less produced"
    - "Similar vibe to X but with more groove"
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM parser.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️  anthropic library not installed. Install with: pip install anthropic")

    def parse(self, feedback: str) -> FeedbackIntent:
        """
        Parse feedback using LLM if available, fallback to pattern matching.

        Args:
            feedback: Natural language feedback string

        Returns:
            FeedbackIntent with extracted information
        """
        if not self.client:
            # Fallback to pattern-based parsing
            from src.feedback import FeedbackAnalyzer
            analyzer = FeedbackAnalyzer()
            return analyzer.parse(feedback)

        # Use LLM for parsing
        return self._parse_with_llm(feedback)

    def _parse_with_llm(self, feedback: str) -> FeedbackIntent:
        """Parse feedback using Claude LLM."""
        prompt = f"""Analyze this music recommendation feedback and extract structured intent.

Feedback: "{feedback}"

Extract and return (as JSON):
{{
  "adjustment_type": "one of: energy_lower, energy_higher, mood_shift, genre_shift, tempo_lower, tempo_higher, overall_softer, overall_harder",
  "target_value": "0.0-1.0 float representing desired state",
  "liked_song": "song title if mentioned, null otherwise",
  "confidence": "0.0-1.0 float on parse confidence",
  "reasoning": "brief explanation of extraction"
}}

Rules:
- If user says "too energetic" or "calmer" → energy_lower
- If user says "more upbeat" or "more intense" → energy_higher
- If user says "softer" or "more relaxing" → overall_softer
- If user says "harder" or "more intense" → overall_harder
- If user says "calmer" specifically, target_value ≈ 0.2-0.4
- If user says "more energetic", target_value ≈ 0.7-0.9
- confidence = 0.9+ if clear, 0.6-0.8 if ambiguous, <0.6 if unclear"""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Parse JSON from response
            import json
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return self._create_intent(parsed, feedback)

        except Exception as e:
            print(f"⚠️  LLM parsing failed: {e}. Using pattern matching instead.")

        # Fallback to pattern-based parsing
        from src.feedback import FeedbackAnalyzer
        analyzer = FeedbackAnalyzer()
        return analyzer.parse(feedback)

    def _create_intent(self, parsed: Dict, original_feedback: str) -> FeedbackIntent:
        """Convert LLM response to FeedbackIntent."""
        # Map string to AdjustmentType
        adjustment_str = parsed.get("adjustment_type", "overall_softer")
        try:
            adjustment_type = AdjustmentType[adjustment_str.upper()]
        except KeyError:
            adjustment_type = AdjustmentType.OVERALL_SOFTER

        return FeedbackIntent(
            liked_song=parsed.get("liked_song"),
            adjustment_type=adjustment_type,
            target_value=float(parsed.get("target_value", 0.5)),
            reason=original_feedback,
            confidence=float(parsed.get("confidence", 0.7)),
        )


class FeedbackParserFactory:
    """Factory for creating appropriate feedback parser."""

    @staticmethod
    def create(use_llm: bool = False) -> "FeedbackAnalyzer or LLMFeedbackParser":
        """
        Create appropriate parser.

        Args:
            use_llm: If True, use LLM parser; if False, use pattern-based

        Returns:
            Parser instance (LLMFeedbackParser or FeedbackAnalyzer)
        """
        if use_llm:
            llm_parser = LLMFeedbackParser()
            if llm_parser.client:
                print("✅ Using LLM-enhanced feedback parser")
                return llm_parser
            else:
                print("⚠️  LLM not available. Using pattern-based parser.")
                from src.feedback import FeedbackAnalyzer
                return FeedbackAnalyzer()
        else:
            from src.feedback import FeedbackAnalyzer
            return FeedbackAnalyzer()
