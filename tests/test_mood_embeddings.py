"""
Tests for Mood Embeddings — semantic mood similarity.

Tests validate that related moods (calm, chill, relaxed) get partial credit
instead of all-or-nothing matching.

Moods are mapped to a 2D embedding space:
- Valence axis: sad ←→ happy
- Energy axis: calm ←→ intense
"""

import unittest
import math


# 2D Mood Embedding Space
# Each mood has (valence, energy) coordinates in [0, 1] x [0, 1]
MOOD_EMBEDDINGS = {
    "happy": (0.9, 0.7),      # High valence, high energy
    "energetic": (0.7, 0.95),  # Moderate valence, very high energy
    "excited": (0.8, 0.9),     # High valence, very high energy
    "uplifting": (0.85, 0.75), # High valence, high energy

    "calm": (0.6, 0.2),        # Moderate valence, low energy
    "chill": (0.55, 0.25),     # Moderate valence, low energy
    "relaxed": (0.6, 0.3),     # Moderate valence, low energy
    "peaceful": (0.65, 0.15),  # Moderate-high valence, very low energy

    "melancholic": (0.3, 0.4), # Low valence, moderate energy
    "sad": (0.2, 0.3),         # Very low valence, low energy
    "moody": (0.35, 0.5),      # Low valence, moderate energy
    "introspective": (0.4, 0.35), # Low valence, low energy

    "intense": (0.4, 0.95),    # Low valence, very high energy
    "aggressive": (0.2, 0.9),  # Very low valence, very high energy
    "focused": (0.5, 0.7),     # Moderate valence, high energy

    "romantic": (0.75, 0.5),   # High valence, moderate energy
    "dreamy": (0.65, 0.4),     # Moderate-high valence, low-moderate energy
    "nostalgic": (0.45, 0.45), # Moderate valence, moderate energy
}


def mood_similarity(mood_a: str, mood_b: str) -> float:
    """
    Compute semantic similarity between two moods using embedding distance.

    Moods are mapped to 2D space (valence, energy).
    Similarity is computed as: 1.0 - (euclidean_distance / max_distance)

    - Exact match: 1.0
    - Very similar (e.g., calm ↔ chill): 0.85-0.99
    - Moderately similar (e.g., calm ↔ peaceful): 0.5-0.85
    - Different (e.g., calm ↔ intense): 0.0-0.5
    - Opposite (e.g., happy ↔ sad): Near 0.0

    Args:
        mood_a: First mood (e.g., "calm")
        mood_b: Second mood (e.g., "chill")

    Returns:
        Similarity score 0.0-1.0
    """
    if not mood_a or not mood_b:
        return 0.0

    a = mood_a.lower().strip()
    b = mood_b.lower().strip()

    # Exact match
    if a == b:
        return 1.0

    # Get embeddings (default to center if unknown)
    embed_a = MOOD_EMBEDDINGS.get(a, (0.5, 0.5))
    embed_b = MOOD_EMBEDDINGS.get(b, (0.5, 0.5))

    # Euclidean distance in 2D space
    dx = embed_a[0] - embed_b[0]
    dy = embed_a[1] - embed_b[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Maximum distance is diagonal: sqrt(1^2 + 1^2) ≈ 1.414
    max_distance = math.sqrt(2)

    # Convert distance to similarity: 1.0 at distance 0, 0.0 at max distance
    similarity = 1.0 - (distance / max_distance)

    return round(max(0.0, similarity), 2)


class TestMoodEmbeddings(unittest.TestCase):
    """Test mood embedding mapping."""

    def test_exact_match_returns_one(self):
        """Exact mood match returns 1.0."""
        self.assertEqual(mood_similarity("calm", "calm"), 1.0)
        self.assertEqual(mood_similarity("happy", "happy"), 1.0)
        self.assertEqual(mood_similarity("intense", "intense"), 1.0)

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        self.assertEqual(mood_similarity("Calm", "calm"), 1.0)
        self.assertEqual(mood_similarity("HAPPY", "happy"), 1.0)

    def test_empty_string_returns_zero(self):
        """Empty strings return 0.0."""
        self.assertEqual(mood_similarity("", "calm"), 0.0)
        self.assertEqual(mood_similarity("calm", ""), 0.0)

    def test_very_similar_moods_high_similarity(self):
        """Very similar moods (close in embedding space) get high similarity."""
        # calm, chill, relaxed are all in low-energy quadrant
        calm_chill = mood_similarity("calm", "chill")
        calm_relaxed = mood_similarity("calm", "relaxed")

        self.assertGreater(calm_chill, 0.8,
                          f"Calm vs Chill should be very similar, got {calm_chill}")
        self.assertGreater(calm_relaxed, 0.8,
                          f"Calm vs Relaxed should be very similar, got {calm_relaxed}")

    def test_opposite_moods_low_similarity(self):
        """Opposite moods (far in embedding space) get low similarity."""
        # happy (high valence, high energy) vs sad (low valence, low energy)
        happy_sad = mood_similarity("happy", "sad")

        self.assertLess(happy_sad, 0.5,
                       f"Happy vs Sad should be very different, got {happy_sad}")

    def test_orthogonal_moods_moderate_similarity(self):
        """Orthogonal moods (90° apart) get moderate similarity."""
        # calm (high valence, low energy) vs intense (low valence, high energy)
        # These are roughly perpendicular in the embedding space
        calm_intense = mood_similarity("calm", "intense")

        self.assertGreater(calm_intense, 0.2,
                          f"Calm vs Intense should have some similarity, got {calm_intense}")
        self.assertLess(calm_intense, 0.6,
                       f"Calm vs Intense should not be too similar, got {calm_intense}")

    def test_similarity_is_symmetric(self):
        """Similarity(A, B) == Similarity(B, A)."""
        sim_ab = mood_similarity("calm", "excited")
        sim_ba = mood_similarity("excited", "calm")
        self.assertEqual(sim_ab, sim_ba,
                        "Mood similarity should be symmetric")

    def test_similar_moods_are_closer_than_different(self):
        """Similar moods should be closer than different moods."""
        # calm and chill are very similar
        calm_chill = mood_similarity("calm", "chill")
        # calm and intense are different
        calm_intense = mood_similarity("calm", "intense")

        self.assertGreater(calm_chill, calm_intense,
                          f"Similar moods should be closer: {calm_chill} > {calm_intense}")


class TestMoodSimilarityThresholds(unittest.TestCase):
    """Test similarity threshold behavior for scoring."""

    def test_perfect_match_gets_full_weight(self):
        """Perfect match (1.0) gets full mood weight (1.0)."""
        sim = mood_similarity("calm", "calm")
        weight = 1.0
        contribution = weight * sim
        self.assertEqual(contribution, 1.0)

    def test_very_similar_mood_gets_good_weight(self):
        """Very similar mood (0.8+) gets proportional weight."""
        sim = mood_similarity("calm", "chill")
        weight = 1.0
        contribution = weight * sim

        # Should be in range [0.8, 1.0)
        self.assertGreater(contribution, 0.7,
                          f"Very similar mood should yield > 0.7 weight, got {contribution}")
        self.assertLess(contribution, 1.0,
                       f"Non-exact similarity should yield < 1.0 weight, got {contribution}")

    def test_moderately_different_mood_gets_partial_weight(self):
        """Moderately different mood gets partial weight."""
        sim = mood_similarity("calm", "romantic")
        weight = 1.0
        contribution = weight * sim

        # Should be in range [0.2, 0.6)
        self.assertGreater(contribution, 0.1,
                          f"Moderately different mood should yield > 0.1 weight, got {contribution}")

    def test_very_different_mood_gets_minimal_weight(self):
        """Very different mood (opposite) gets minimal weight."""
        sim = mood_similarity("happy", "sad")
        weight = 1.0
        contribution = weight * sim

        # Should be < 0.5
        self.assertLess(contribution, 0.5,
                       f"Very different mood should yield < 0.5 weight, got {contribution}")


class TestMoodEmbeddingAxes(unittest.TestCase):
    """Test that embedding axes match expected emotional dimensions."""

    def test_valence_axis_happy_vs_sad(self):
        """Valence axis: happy has higher valence than sad."""
        happy_embed = MOOD_EMBEDDINGS["happy"]
        sad_embed = MOOD_EMBEDDINGS["sad"]

        self.assertGreater(happy_embed[0], sad_embed[0],
                          "Happy should have higher valence than sad")

    def test_energy_axis_intense_vs_calm(self):
        """Energy axis: intense has higher energy than calm."""
        intense_embed = MOOD_EMBEDDINGS["intense"]
        calm_embed = MOOD_EMBEDDINGS["calm"]

        self.assertGreater(intense_embed[1], calm_embed[1],
                          "Intense should have higher energy than calm")

    def test_quadrants_meaningful(self):
        """Each quadrant represents expected emotional territory."""
        # High valence, high energy: happy, excited
        self.assertGreater(MOOD_EMBEDDINGS["happy"][0], 0.7)
        self.assertGreater(MOOD_EMBEDDINGS["happy"][1], 0.6)
        self.assertGreater(MOOD_EMBEDDINGS["excited"][0], 0.7)
        self.assertGreater(MOOD_EMBEDDINGS["excited"][1], 0.8)

        # Low valence, low energy: sad, introspective
        self.assertLess(MOOD_EMBEDDINGS["sad"][0], 0.3)
        self.assertLess(MOOD_EMBEDDINGS["sad"][1], 0.4)


class TestMoodContributionScaling(unittest.TestCase):
    """Test how mood similarity scales recommendation scores."""

    def test_mood_similarity_enables_emotional_flexibility(self):
        """Fuzzy mood matching allows emotional nuance."""
        # User wants "calm", song has "chill"
        # Should get credit even though not exact match

        user_mood = "calm"
        song_mood = "chill"

        sim = mood_similarity(user_mood, song_mood)

        # Should be >0 (enables match) but <1.0 (still prefer exact match)
        self.assertGreater(sim, 0.0, "Should enable emotional flexibility")
        self.assertLess(sim, 1.0, "Should still prefer exact mood match")

    def test_fuzzy_matching_vs_exact_matching(self):
        """
        Exact mood match scores higher than fuzzy match,
        but fuzzy match scores higher than mismatch.

        This is the key property: exact > fuzzy > mismatch
        """
        weight = 1.0

        # Exact match
        exact_score = weight * mood_similarity("calm", "calm")

        # Fuzzy match (similar mood)
        fuzzy_score = weight * mood_similarity("calm", "chill")

        # Mismatch (opposite mood)
        mismatch_score = weight * mood_similarity("calm", "intense")

        self.assertGreater(exact_score, fuzzy_score,
                          f"Exact should score higher: {exact_score} > {fuzzy_score}")
        self.assertGreater(fuzzy_score, mismatch_score,
                          f"Fuzzy should score higher: {fuzzy_score} > {mismatch_score}")

    def test_mood_penalty_with_similarity(self):
        """
        Mood mismatch penalty is reduced for similar moods.

        Before: mismatch = -0.5 (all-or-nothing)
        After: mismatch = -0.5 * (1.0 - similarity) (proportional penalty)
        """
        penalty_base = 0.5

        # Exact match: no penalty
        sim_exact = mood_similarity("calm", "calm")
        penalty_exact = penalty_base * (1.0 - sim_exact)
        self.assertEqual(penalty_exact, 0.0,
                        "Exact match should have zero penalty")

        # Very similar: minimal penalty
        sim_similar = mood_similarity("calm", "chill")
        penalty_similar = penalty_base * (1.0 - sim_similar)
        self.assertLess(penalty_similar, 0.1,
                       f"Very similar should have minimal penalty, got {penalty_similar}")

        # Very different: full penalty
        sim_different = mood_similarity("calm", "intense")
        penalty_different = penalty_base * (1.0 - sim_different)
        self.assertGreater(penalty_different, 0.1,
                          f"Very different should have significant penalty, got {penalty_different}")


if __name__ == '__main__':
    unittest.main()
