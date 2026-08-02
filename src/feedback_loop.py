"""
Agentic Feedback Loop — Orchestrates the full feedback → learning cycle.

This implements the complete Plan → Act → Validate → Learn workflow:

1. PLAN (Analyzer):   Parse feedback → extract intent
2. ACT (Search):      Find recommendations with adjusted weights
3. VALIDATE (Validator): Check if recommendations match feedback
4. LEARN (Learner):   Update embeddings based on validation
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from src.feedback import FeedbackAnalyzer, FeedbackIntent
from src.learner import FeedbackValidator, FeedbackMemory, EmbeddingLearner
from src.recommender import Recommender, UserProfile

logger = logging.getLogger(__name__)


@dataclass
class FeedbackLoopResult:
    """Result of one feedback loop iteration."""
    original_recommendations: List[str]  # Top-3 song titles
    adjusted_recommendations: List[str]  # Top-3 song titles after feedback
    feedback_intent: FeedbackIntent
    validation_passed: bool
    validation_confidence: float
    validation_reason: str
    embeddings_updated: Dict[str, float]  # Changes made


class FeedbackLoop:
    """
    Orchestrates the complete agentic feedback loop.

    Implements: Plan → Act → Validate → Learn

    Example usage:
        loop = FeedbackLoop(recommender, learner)
        result = loop.process_feedback(
            user_profile=user,
            feedback="I liked that song but wanted something calmer"
        )
        print(f"Validation: {result.validation_passed}")
        print(f"Updated embeddings: {result.embeddings_updated}")
    """

    def __init__(self, recommender: Recommender, learner: Optional[EmbeddingLearner] = None):
        self.recommender = recommender
        self.learner = learner or EmbeddingLearner()
        self.analyzer = FeedbackAnalyzer()
        self.history: List[FeedbackLoopResult] = []

    def process_feedback(
        self,
        user_profile: UserProfile,
        feedback: str,
        k: int = 5,
    ) -> FeedbackLoopResult:
        """
        Process user feedback through the complete agentic loop.

        Plan → Act → Validate → Learn

        Args:
            user_profile: User's original preferences
            feedback: Natural language feedback string
            k: Number of recommendations to generate

        Returns:
            FeedbackLoopResult with all details
        """

        # PLAN: Analyze feedback
        intent = self.analyzer.parse(feedback)
        logger.info(f"📋 PLAN: Parsed feedback intent: {intent.adjustment_type}")

        # Get original recommendations (baseline)
        original_user_dict = {
            'genre': user_profile.favorite_genre,
            'mood': user_profile.favorite_mood,
            'energy': user_profile.target_energy,
            'valence': user_profile.preferred_valence,
            'danceability': user_profile.preferred_danceability,
            'tempo_bpm': user_profile.preferred_tempo_bpm,
            'acousticness': user_profile.preferred_acousticness,
            'min_popularity': user_profile.min_popularity,
            'production_quality': user_profile.preferred_production_quality,
            'artist_familiarity': user_profile.prefer_artist_familiarity and 0.7 or 0.3,
        }

        original_recs = self.recommender.recommend(user_profile, k=k)
        original_titles = [f"{s.title}" for s in original_recs]
        logger.info(f"🎯 Original recommendations: {', '.join(original_titles[:3])}")

        # ACT: Apply feedback to adjust user preferences
        adjusted_prefs = self.analyzer.apply_to_profile(intent, original_user_dict)
        logger.info(f"⚙️  ACT: Adjusted preferences applied")

        # Create modified user profile for adjusted recommendations
        adjusted_user = UserProfile(
            favorite_genre=adjusted_prefs.get('genre', user_profile.favorite_genre),
            favorite_mood=adjusted_prefs.get('mood', user_profile.favorite_mood),
            target_energy=adjusted_prefs.get('energy', user_profile.target_energy),
            preferred_valence=adjusted_prefs.get('valence', user_profile.preferred_valence),
            preferred_danceability=adjusted_prefs.get('danceability', user_profile.preferred_danceability),
            preferred_tempo_bpm=adjusted_prefs.get('tempo_bpm', user_profile.preferred_tempo_bpm),
            preferred_acousticness=adjusted_prefs.get('acousticness', user_profile.preferred_acousticness),
            min_popularity=adjusted_prefs.get('min_popularity', user_profile.min_popularity),
            preferred_production_quality=adjusted_prefs.get('production_quality', user_profile.preferred_production_quality),
            prefer_artist_familiarity=user_profile.prefer_artist_familiarity,
        )

        adjusted_recs = self.recommender.recommend(adjusted_user, k=k)
        adjusted_titles = [f"{s.title}" for s in adjusted_recs]
        logger.info(f"📝 Adjusted recommendations: {', '.join(adjusted_titles[:3])}")

        # Convert to dicts for validation
        original_song_dicts = [
            {
                'title': s.title,
                'energy': s.energy,
                'valence': s.valence,
                'mood': s.mood,
                'tempo_bpm': s.tempo_bpm,
            }
            for s in original_recs
        ]
        adjusted_song_dicts = [
            {
                'title': s.title,
                'energy': s.energy,
                'valence': s.valence,
                'mood': s.mood,
                'tempo_bpm': s.tempo_bpm,
            }
            for s in adjusted_recs
        ]

        # VALIDATE: Check if recommendations actually match feedback intent
        validation_passed, validation_conf, validation_reason = FeedbackValidator.validate_recommendation(
            original_song_dicts,
            adjusted_song_dicts,
            intent.adjustment_type.value,
        )
        logger.info(f"✓ VALIDATE: {validation_reason} (confidence: {validation_conf:.2f})")

        # LEARN: Update embeddings if validation passed
        embeddings_updated = {}
        if validation_passed and validation_conf > 0.6:
            memory = FeedbackMemory(
                feedback_text=feedback,
                adjustment_type=intent.adjustment_type.value,
                original_preferences=original_user_dict,
                adjusted_preferences=adjusted_prefs,
                recommended_songs=adjusted_titles[:3],
                user_validated=True,
                validation_reason=validation_reason,
            )
            self.learner.record_feedback(memory)
            embeddings_updated = self.learner.learn_from_validated_feedback(memory)
            logger.info(f"🧠 LEARN: Updated {len(embeddings_updated)} embedding coordinates")
        else:
            logger.info(f"⏭️  LEARN: Skipped (validation not confident enough)")

        # Build result
        result = FeedbackLoopResult(
            original_recommendations=original_titles,
            adjusted_recommendations=adjusted_titles,
            feedback_intent=intent,
            validation_passed=validation_passed,
            validation_confidence=validation_conf,
            validation_reason=validation_reason,
            embeddings_updated=embeddings_updated,
        )

        self.history.append(result)
        return result

    def get_history(self) -> List[FeedbackLoopResult]:
        """Return history of all feedback iterations."""
        return self.history

    def get_learning_stats(self) -> Dict[str, any]:
        """Get learning statistics."""
        return self.learner.get_learning_summary()
