"""
Feedback Analyzer — Parses user feedback to extract actionable insights.

This module handles the "Plan" phase of the agentic loop:
- Parse natural language feedback: "I liked Song X but it was too energetic"
- Extract structured intent: FeedbackIntent { song, adjustment_type, target_value }
- Prepare instructions for the Search Agent to act on
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import re


class AdjustmentType(Enum):
    """Types of adjustments user can request."""
    ENERGY_LOWER = "energy_lower"          # "calmer", "less energetic"
    ENERGY_HIGHER = "energy_higher"        # "more energetic", "less calm"
    MOOD_SHIFT = "mood_shift"              # "more happy", "less intense"
    GENRE_SHIFT = "genre_shift"            # "more electronic", "less rock"
    TEMPO_LOWER = "tempo_lower"            # "slower"
    TEMPO_HIGHER = "tempo_higher"          # "faster"
    OVERALL_SOFTER = "overall_softer"      # "softer", "more relaxing"
    OVERALL_HARDER = "overall_harder"      # "harder", "more intense"


@dataclass
class FeedbackIntent:
    """Structured representation of user feedback."""
    liked_song: Optional[str]               # Song title they liked (or None if disliked)
    adjustment_type: AdjustmentType         # What to adjust
    target_value: float                     # Target value (0.0-1.0) or magnitude
    reason: str                             # Why they gave this feedback
    confidence: float                       # Confidence in parse (0.0-1.0)


class FeedbackAnalyzer:
    """
    Parses user feedback and extracts structured intent.

    Examples:
    - "I liked Song X but it was too energetic"
      → FeedbackIntent(liked_song="Song X", adjustment=ENERGY_LOWER, target=0.3)

    - "Give me something more calm than Song Y"
      → FeedbackIntent(liked_song="Song Y", adjustment=MOOD_SHIFT, target=0.8)

    - "I want less intense music"
      → FeedbackIntent(liked_song=None, adjustment=OVERALL_SOFTER, target=0.3)
    """

    # Keyword patterns for energy adjustment
    ENERGY_LOWER_PATTERNS = [
        r"(too energetic|less energetic|less intense|calmer|more calm|more relaxed|chill|slow down)",
        r"(too (fast|high energy)|tone down|reduce energy)",
    ]

    ENERGY_HIGHER_PATTERNS = [
        r"(more energetic|more intense|more upbeat|faster|higher energy)",
        r"(less calm|less relaxed|pump it up)",
    ]

    # Mood patterns
    MOOD_SHIFT_PATTERNS = {
        "happy": r"(more happy|happier|more uplifting|more positive|more upbeat)",
        "sad": r"(more sad|sadder|more melancholic|more introspective)",
        "calm": r"(more calm|calmer|more peaceful|more serene)",
        "intense": r"(more intense|intensify|more aggressive)",
        "romantic": r"(more romantic|romantic|love)",
    }

    # Genre patterns
    GENRE_SHIFT_PATTERNS = {
        "electronic": r"(more electronic|electronic vibes|synth)",
        "acoustic": r"(more acoustic|acoustic feel|unplugged)",
        "rock": r"(more rock|rock vibes|guitar-driven)",
        "lofi": r"(more lofi|lo-fi|chill hip-hop)",
        "pop": r"(more pop|poppy|mainstream)",
    }

    # Overall softness/hardness
    SOFTER_PATTERNS = r"(softer|more relaxing|less harsh|smoother|cozier)"
    HARDER_PATTERNS = r"(harder|more intense|less relaxing|grittier|heavier)"

    def parse(self, feedback: str) -> FeedbackIntent:
        """
        Parse user feedback and extract structured intent.

        Args:
            feedback: Natural language feedback string

        Returns:
            FeedbackIntent with extracted information
        """
        feedback_lower = feedback.lower().strip()

        # Step 1: Extract song title if mentioned
        liked_song = self._extract_song_title(feedback)

        # Step 2: Detect adjustment type (highest confidence wins)
        adjustment, confidence = self._detect_adjustment(feedback_lower)

        # Step 3: Extract target value based on adjustment type
        target_value = self._extract_target_value(adjustment, feedback_lower)

        # Step 4: Reason is the feedback itself
        reason = feedback

        return FeedbackIntent(
            liked_song=liked_song,
            adjustment_type=adjustment,
            target_value=target_value,
            reason=reason,
            confidence=confidence,
        )

    def _extract_song_title(self, feedback: str) -> Optional[str]:
        """Extract song title from feedback. Heuristic: quoted text or after 'song'."""
        # Look for quoted song titles
        quoted = re.search(r'["\']([^"\']+)["\']', feedback)
        if quoted:
            return quoted.group(1)

        # Look for "song X" pattern
        song_pattern = re.search(r'(?:song|track)\s+([A-Z][^,.\n]+)', feedback, re.IGNORECASE)
        if song_pattern:
            return song_pattern.group(1).strip()

        # Look for patterns like "like X" or "liked X"
        like_pattern = re.search(r'(?:like|liked)\s+(?:song\s+)?([A-Z][^,.\n]+?)(?:\s+but|\s+however|$)', feedback, re.IGNORECASE)
        if like_pattern:
            return like_pattern.group(1).strip()

        return None

    def _detect_adjustment(self, feedback: str) -> tuple[AdjustmentType, float]:
        """Detect adjustment type from feedback patterns."""
        # Check energy patterns first (highest priority)
        for pattern in self.ENERGY_LOWER_PATTERNS:
            if re.search(pattern, feedback):
                return AdjustmentType.ENERGY_LOWER, 0.95

        for pattern in self.ENERGY_HIGHER_PATTERNS:
            if re.search(pattern, feedback):
                return AdjustmentType.ENERGY_HIGHER, 0.95

        # Check overall softness/hardness patterns
        if re.search(self.SOFTER_PATTERNS, feedback):
            return AdjustmentType.OVERALL_SOFTER, 0.90

        if re.search(self.HARDER_PATTERNS, feedback):
            return AdjustmentType.OVERALL_HARDER, 0.90

        # Check mood patterns
        for mood, pattern in self.MOOD_SHIFT_PATTERNS.items():
            if re.search(pattern, feedback):
                return AdjustmentType.MOOD_SHIFT, 0.85

        # Check genre patterns
        for genre, pattern in self.GENRE_SHIFT_PATTERNS.items():
            if re.search(pattern, feedback):
                return AdjustmentType.GENRE_SHIFT, 0.80

        # Default to energy adjustment if not specific
        if "energy" in feedback or "intense" in feedback or "calm" in feedback:
            return AdjustmentType.ENERGY_LOWER, 0.70

        return AdjustmentType.OVERALL_SOFTER, 0.50

    def _extract_target_value(self, adjustment: AdjustmentType, feedback: str) -> float:
        """
        Extract target value based on adjustment type.

        Returns a value 0.0-1.0 representing the desired state:
        - 0.0 = minimum (very calm, very slow)
        - 1.0 = maximum (very energetic, very fast)
        """
        # Look for intensity words
        very_keywords = ["very", "much", "really", "extremely"]
        is_very = any(kw in feedback for kw in very_keywords)

        if adjustment == AdjustmentType.ENERGY_LOWER:
            return 0.2 if is_very else 0.4
        elif adjustment == AdjustmentType.ENERGY_HIGHER:
            return 0.8 if is_very else 0.6
        elif adjustment == AdjustmentType.MOOD_SHIFT:
            return 0.8 if is_very else 0.6
        elif adjustment == AdjustmentType.OVERALL_SOFTER:
            return 0.3 if is_very else 0.4
        elif adjustment == AdjustmentType.OVERALL_HARDER:
            return 0.7 if is_very else 0.6
        else:
            return 0.5

    def apply_to_profile(self, intent: FeedbackIntent, user_prefs: Dict) -> Dict:
        """
        Apply feedback intent to user profile, returning adjusted preferences.

        This is the "Act" phase: modify the user profile based on feedback.

        Args:
            intent: Parsed feedback intent
            user_prefs: Original user preferences dict

        Returns:
            Modified user preferences dict
        """
        adjusted = dict(user_prefs)

        if intent.adjustment_type == AdjustmentType.ENERGY_LOWER:
            adjusted['energy'] = intent.target_value
            adjusted['tempo_bpm'] = intent.target_value * 120  # Scale to 0-120 BPM range

        elif intent.adjustment_type == AdjustmentType.ENERGY_HIGHER:
            adjusted['energy'] = intent.target_value
            adjusted['tempo_bpm'] = intent.target_value * 200  # Scale to up to 200 BPM

        elif intent.adjustment_type == AdjustmentType.MOOD_SHIFT:
            # Shift mood towards target mood
            # For simplicity, adjust valence and energy towards target
            if "happy" in intent.reason:
                adjusted['valence'] = 0.8
            elif "sad" in intent.reason:
                adjusted['valence'] = 0.2
            elif "calm" in intent.reason:
                adjusted['energy'] = 0.2
            elif "intense" in intent.reason:
                adjusted['energy'] = 0.9

        elif intent.adjustment_type == AdjustmentType.OVERALL_SOFTER:
            adjusted['energy'] = intent.target_value
            adjusted['valence'] = 0.7  # Slightly positive
            adjusted['acousticness'] = 0.7  # More acoustic

        elif intent.adjustment_type == AdjustmentType.OVERALL_HARDER:
            adjusted['energy'] = intent.target_value
            adjusted['valence'] = 0.5  # Neutral to slightly dark
            adjusted['danceability'] = 0.8  # Danceable/rhythmic

        elif intent.adjustment_type == AdjustmentType.TEMPO_LOWER:
            adjusted['tempo_bpm'] = min(90, adjusted.get('tempo_bpm', 100))

        elif intent.adjustment_type == AdjustmentType.TEMPO_HIGHER:
            adjusted['tempo_bpm'] = max(140, adjusted.get('tempo_bpm', 100))

        elif intent.adjustment_type == AdjustmentType.GENRE_SHIFT:
            # Would need more context to shift genre, skip for now
            pass

        return adjusted


# Quick utility for common feedback patterns
def parse_feedback(feedback: str) -> FeedbackIntent:
    """Convenience function to parse feedback."""
    analyzer = FeedbackAnalyzer()
    return analyzer.parse(feedback)
