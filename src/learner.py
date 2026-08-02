"""
Learning Module — Updates embeddings based on validated user feedback.

This module handles the "Learn" phase of the agentic loop:
- Track feedback success/failure
- Update mood embeddings and genre relationships based on patterns
- Adjust weights dynamically as system learns user preferences
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List
import math
import copy


@dataclass
class FeedbackMemory:
    """Records a single feedback iteration and its outcome."""
    feedback_text: str
    adjustment_type: str
    original_preferences: Dict
    adjusted_preferences: Dict
    recommended_songs: List[str]  # Top-3 song titles
    user_validated: bool          # Did user accept the recommendations?
    validation_reason: Optional[str] = None


@dataclass
class EmbeddingLearner:
    """
    Learns from validated feedback and updates embedding coordinates.

    Strategy:
    1. User gives feedback: "I liked calm songs but this was too energetic"
    2. System recommends with adjusted energy preference
    3. User validates: "Yes, these are better!"
    4. Learner updates MOOD_EMBEDDINGS to move "calm" down the energy axis
    5. Future recommendations for "calm" users improve

    Learning is conservative: only update when validation is high confidence.
    """

    memory: List[FeedbackMemory] = field(default_factory=list)
    mood_embeddings: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    genre_relationships: Dict[str, List[str]] = field(default_factory=dict)
    learning_rate: float = 0.05  # Conservative: small updates per feedback

    def __post_init__(self):
        """Initialize learner with current embeddings."""
        # Import here to avoid circular dependency
        from src.recommender import MOOD_EMBEDDINGS, GENRE_RELATIONSHIPS

        self.mood_embeddings = copy.deepcopy(MOOD_EMBEDDINGS)
        self.genre_relationships = copy.deepcopy(GENRE_RELATIONSHIPS)

    def record_feedback(self, memory: FeedbackMemory) -> None:
        """Record a feedback iteration in memory."""
        self.memory.append(memory)

    def learn_from_validated_feedback(self, memory: FeedbackMemory) -> Dict[str, float]:
        """
        Learn from validated feedback and update embeddings.

        Returns:
            Dictionary of updates made: {"mood:calm:valence": +0.02, ...}
        """
        if not memory.user_validated:
            return {}  # Only learn from positive validation

        updates = {}

        # Parse the adjustment type to understand what changed
        # energy_lower → move mood down on energy axis
        # energy_higher → move mood up on energy axis
        # etc.

        if "energy_lower" in memory.adjustment_type:
            updates = self._learn_energy_shift(
                memory.original_preferences,
                memory.adjusted_preferences,
                direction=-1,  # Lower energy
            )

        elif "energy_higher" in memory.adjustment_type:
            updates = self._learn_energy_shift(
                memory.original_preferences,
                memory.adjusted_preferences,
                direction=1,  # Higher energy
            )

        elif "mood" in memory.adjustment_type:
            updates = self._learn_mood_shift(
                memory.original_preferences,
                memory.adjusted_preferences,
            )

        return updates

    def _learn_energy_shift(self, orig_prefs: Dict, adj_prefs: Dict, direction: int) -> Dict[str, float]:
        """
        User validated that energy adjustment helped.
        Move the user's favorite mood along the energy axis.

        direction: -1 for lower energy, +1 for higher energy
        """
        updates = {}
        mood = orig_prefs.get('mood', '').lower()

        if mood not in self.mood_embeddings:
            return updates

        valence, energy = self.mood_embeddings[mood]

        # Move energy axis based on validation
        new_energy = energy + (self.learning_rate * direction)
        new_energy = max(0.0, min(1.0, new_energy))  # Clamp to [0, 1]

        if new_energy != energy:
            self.mood_embeddings[mood] = (valence, new_energy)
            updates[f"mood:{mood}:energy"] = new_energy - energy

        return updates

    def _learn_mood_shift(self, orig_prefs: Dict, adj_prefs: Dict) -> Dict[str, float]:
        """
        User validated that mood shift helped.
        Update valence and energy based on feedback.
        """
        updates = {}
        mood = orig_prefs.get('mood', '').lower()

        if mood not in self.mood_embeddings:
            return updates

        valence, energy = self.mood_embeddings[mood]

        # Adjust based on new preferences
        new_valence = adj_prefs.get('valence', valence)
        new_energy = adj_prefs.get('energy', energy)

        # Move towards adjusted preference, but conservatively
        if new_valence != valence:
            delta = (new_valence - valence) * self.learning_rate
            updated_valence = valence + delta
            updated_valence = max(0.0, min(1.0, updated_valence))
            self.mood_embeddings[mood] = (updated_valence, energy)
            updates[f"mood:{mood}:valence"] = updated_valence - valence

        if new_energy != energy:
            delta = (new_energy - energy) * self.learning_rate
            updated_energy = energy + delta
            updated_energy = max(0.0, min(1.0, updated_energy))
            self.mood_embeddings[mood] = (self.mood_embeddings[mood][0], updated_energy)
            updates[f"mood:{mood}:energy"] = updated_energy - energy

        return updates

    def get_current_embeddings(self) -> Tuple[Dict, Dict]:
        """Return current mood embeddings and genre relationships."""
        return copy.deepcopy(self.mood_embeddings), copy.deepcopy(self.genre_relationships)

    def get_learning_summary(self) -> Dict[str, any]:
        """
        Summary of what the system has learned.

        Returns:
            Dict with statistics on mood adjustments, convergence, etc.
        """
        if not self.memory:
            return {
                "feedback_count": 0,
                "validated_count": 0,
                "accuracy": 0.0,
                "embeddings_updated": 0,
            }

        validated = sum(1 for m in self.memory if m.user_validated)
        accuracy = validated / len(self.memory) if self.memory else 0.0

        # Count how many mood embeddings changed
        from src.recommender import MOOD_EMBEDDINGS

        embeddings_changed = sum(
            1
            for mood, coord in self.mood_embeddings.items()
            if mood in MOOD_EMBEDDINGS and MOOD_EMBEDDINGS[mood] != coord
        )

        return {
            "feedback_count": len(self.memory),
            "validated_count": validated,
            "accuracy": accuracy,
            "embeddings_updated": embeddings_changed,
            "learning_rate": self.learning_rate,
        }


class FeedbackValidator:
    """
    Validates whether recommendations match feedback intent.

    This is the "Validate" phase: check if the system acted correctly on feedback.

    Strategy:
    1. User gives feedback: "I want calmer songs"
    2. System recommends songs with lower energy
    3. Validator checks: Do recommended songs have lower average energy than previous?
    4. If yes: validation=True, learner can update embeddings
    5. If no: validation=False, learner skips this feedback
    """

    @staticmethod
    def validate_energy_adjustment(
        original_songs: List[Dict],
        adjusted_songs: List[Dict],
        direction: str,  # "lower" or "higher"
    ) -> Tuple[bool, float]:
        """
        Validate that energy adjustment was applied correctly.

        Args:
            original_songs: Top-k songs from original preferences
            adjusted_songs: Top-k songs from adjusted preferences
            direction: "lower" (should have lower energy) or "higher"

        Returns:
            (validation_passed, confidence_score)
        """
        if not original_songs or not adjusted_songs:
            return False, 0.0

        orig_energy = sum(s.get('energy', 0.5) for s in original_songs) / len(original_songs)
        adj_energy = sum(s.get('energy', 0.5) for s in adjusted_songs) / len(adjusted_songs)

        if direction == "lower":
            passed = adj_energy < orig_energy
            confidence = max(0.0, 1.0 - (adj_energy - orig_energy + 0.5))  # 0.5 = threshold
        else:  # higher
            passed = adj_energy > orig_energy
            confidence = max(0.0, 1.0 - (orig_energy - adj_energy + 0.5))

        return passed, min(1.0, confidence)

    @staticmethod
    def validate_mood_adjustment(
        original_songs: List[Dict],
        adjusted_songs: List[Dict],
    ) -> Tuple[bool, float]:
        """
        Validate that mood adjustment was applied correctly.

        Since we don't have direct mood similarity scores for all songs,
        use energy/valence as proxies.
        """
        if not original_songs or not adjusted_songs:
            return False, 0.0

        # Check if adjusted songs have different emotional profiles
        orig_valence = sum(s.get('valence', 0.5) for s in original_songs) / len(original_songs)
        adj_valence = sum(s.get('valence', 0.5) for s in adjusted_songs) / len(adjusted_songs)

        valence_changed = abs(adj_valence - orig_valence) > 0.1
        confidence = 0.8 if valence_changed else 0.4

        return valence_changed, confidence

    @staticmethod
    def validate_recommendation(
        original_songs: List[Dict],
        adjusted_songs: List[Dict],
        adjustment_type: str,
    ) -> Tuple[bool, float, str]:
        """
        Comprehensive validation of recommendation quality.

        Args:
            original_songs: Baseline recommendations
            adjusted_songs: Recommendations with feedback applied
            adjustment_type: Type of adjustment (energy_lower, mood_shift, etc.)

        Returns:
            (passed, confidence, reason)
        """
        if "energy_lower" in adjustment_type:
            passed, conf = FeedbackValidator.validate_energy_adjustment(
                original_songs, adjusted_songs, "lower"
            )
            reason = "Energy decreased" if passed else "Energy unchanged"

        elif "energy_higher" in adjustment_type:
            passed, conf = FeedbackValidator.validate_energy_adjustment(
                original_songs, adjusted_songs, "higher"
            )
            reason = "Energy increased" if passed else "Energy unchanged"

        elif "mood" in adjustment_type:
            passed, conf = FeedbackValidator.validate_mood_adjustment(
                original_songs, adjusted_songs
            )
            reason = "Mood profile changed" if passed else "Mood profile unchanged"

        else:
            passed, conf = True, 0.5
            reason = "Unknown adjustment type"

        return passed, conf, reason
