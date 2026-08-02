"""
Tests for Semantic Genre Similarity — fuzzy genre matching.

Tests validate that related genres get partial credit rather than all-or-nothing matching.
Example: "synthwave" should get partial credit for matching "electronic".
"""

import unittest
from difflib import SequenceMatcher


# Genre relationship graph: explicit semantic relationships
GENRE_RELATIONSHIPS = {
    "pop": ["synth-pop", "indie-pop"],
    "rock": ["metal", "indie-rock", "alternative"],
    "electronic": ["synthwave", "synth-pop", "edm", "house", "techno"],
    "lofi": ["lo-fi", "chill-hop"],
    "hip-hop": ["trap", "rap"],
    "jazz": ["smooth-jazz", "bebop"],
    "indie": ["indie-rock", "indie-pop"],
}


def genre_similarity(genre_a: str, genre_b: str) -> float:
    """
    Compute semantic similarity between two genres (0.0 to 1.0).

    Uses a hybrid approach:
    1. Check explicit genre relationships (high confidence)
    2. Fallback to string similarity if not in relationships
    3. Normalize by string length to handle substrings

    - Exact match: 1.0
    - Related genres: 0.6-0.9
    - Similar strings: 0.3-0.6
    - Different: 0.0-0.3

    Args:
        genre_a: First genre (e.g., "electronic")
        genre_b: Second genre (e.g., "synthwave")

    Returns:
        Similarity score 0.0-1.0
    """
    if not genre_a or not genre_b:
        return 0.0

    # Normalize to lowercase
    a = genre_a.lower().strip()
    b = genre_b.lower().strip()

    # Exact match
    if a == b:
        return 1.0

    # Check explicit relationships (bidirectional)
    if a in GENRE_RELATIONSHIPS and b in GENRE_RELATIONSHIPS[a]:
        return 0.75  # High similarity for known relationships
    if b in GENRE_RELATIONSHIPS and a in GENRE_RELATIONSHIPS[b]:
        return 0.75

    # String similarity: weight by length to prefer longer matches
    string_sim = SequenceMatcher(None, a, b).ratio()

    # Boost similarity if one genre contains a keyword from the other
    # E.g., "synth-pop" contains "synth", so it's similar to "synthwave"
    a_words = set(a.split("-"))
    b_words = set(b.split("-"))
    shared_words = a_words & b_words

    if shared_words:
        # Shared keywords boost similarity
        keyword_boost = 0.3 * len(shared_words) / max(len(a_words), len(b_words))
        string_sim = min(1.0, string_sim + keyword_boost)

    return round(string_sim, 2)


class TestGenreSimilarity(unittest.TestCase):
    """Test the genre similarity function."""

    def test_exact_match_returns_one(self):
        """Exact genre match returns 1.0."""
        self.assertEqual(genre_similarity("pop", "pop"), 1.0)
        self.assertEqual(genre_similarity("rock", "rock"), 1.0)
        self.assertEqual(genre_similarity("lofi", "lofi"), 1.0)

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        self.assertEqual(genre_similarity("Pop", "pop"), 1.0)
        self.assertEqual(genre_similarity("ROCK", "rock"), 1.0)
        self.assertEqual(genre_similarity("LoFi", "lofi"), 1.0)

    def test_very_different_genres_get_zero(self):
        """Very different genres get ~0.0."""
        sim = genre_similarity("pop", "metal")
        self.assertLess(sim, 0.3, f"Pop vs Metal should be very different, got {sim}")

    def test_similar_genres_get_partial_credit(self):
        """Similar genres get partial credit (0.5-0.9)."""
        # Electronic variants
        electronic_synth = genre_similarity("electronic", "synthwave")
        self.assertGreater(electronic_synth, 0.5, "Electronic vs Synthwave should be somewhat similar")
        self.assertLess(electronic_synth, 1.0, "Electronic vs Synthwave should not be exact")

        # Rock variants
        rock_metal = genre_similarity("rock", "metal")
        self.assertGreater(rock_metal, 0.5, "Rock vs Metal should share some similarity")

    def test_substring_match_increases_similarity(self):
        """Genres that share substrings get higher similarity."""
        # "synth-pop" and "synthwave" both contain "synth"
        synth_pop_wave = genre_similarity("synth-pop", "synthwave")
        pop_wave = genre_similarity("pop", "synthwave")

        self.assertGreater(synth_pop_wave, pop_wave,
                          "Synth-pop should be closer to synthwave than pop is")

    def test_empty_string_returns_zero(self):
        """Empty strings return 0.0."""
        self.assertEqual(genre_similarity("", "pop"), 0.0)
        self.assertEqual(genre_similarity("pop", ""), 0.0)
        self.assertEqual(genre_similarity("", ""), 0.0)

    def test_similarity_is_symmetric(self):
        """Similarity(A, B) == Similarity(B, A)."""
        sim_ab = genre_similarity("pop", "rock")
        sim_ba = genre_similarity("rock", "pop")
        self.assertEqual(sim_ab, sim_ba, "Genre similarity should be symmetric")


class TestGenreSimilarityThresholds(unittest.TestCase):
    """Test similarity threshold behavior for scoring."""

    def test_perfect_match_gets_full_weight(self):
        """Perfect match (>0.95) gets full genre weight (2.3)."""
        sim = genre_similarity("pop", "pop")
        weight = 2.3
        contribution = weight * sim
        self.assertEqual(contribution, 2.3)

    def test_high_similarity_gets_good_weight(self):
        """High similarity (0.7-0.95) gets proportional weight."""
        # Example: "synth-pop" vs "synthwave" might be ~0.6-0.7
        sim = genre_similarity("synth-pop", "synthwave")
        weight = 2.3
        contribution = weight * sim

        # Should be in range [1.4, 2.3) (roughly 0.6-1.0 of full weight)
        self.assertGreater(contribution, 1.0,
                          f"Good genre similarity should yield > 1.0 weight, got {contribution}")
        self.assertLess(contribution, 2.3,
                       f"Non-exact similarity should yield < 2.3 weight, got {contribution}")

    def test_low_similarity_gets_minimal_weight(self):
        """Low similarity (<0.4) contributes minimally."""
        sim = genre_similarity("pop", "metal")
        weight = 2.3
        contribution = weight * sim

        # Should be < 1.0 (not worthless, but small)
        self.assertLess(contribution, 1.0,
                       f"Low genre similarity should yield < 1.0 weight, got {contribution}")

    def test_zero_similarity_gets_zero_weight(self):
        """Zero similarity contributes nothing."""
        sim = genre_similarity("pop", "")
        weight = 2.3
        contribution = weight * sim
        self.assertEqual(contribution, 0.0)


class TestGenreContributionScaling(unittest.TestCase):
    """Test how genre similarity scales recommendation scores."""

    def test_genre_similarity_enables_discovery(self):
        """Fuzzy genre matching allows cross-genre discovery."""
        # Example: "synthwave" song for "electronic" preference
        # Should get partial credit, enabling discovery while respecting preference

        user_genre = "electronic"
        song_genre = "synthwave"

        sim = genre_similarity(user_genre, song_genre)

        # Should be >0 (enables discovery) but <1.0 (still prefer exact match)
        self.assertGreater(sim, 0.0, "Should enable cross-genre discovery")
        self.assertLess(sim, 1.0, "Should still prefer exact genre match")

    def test_fuzzy_matching_score_vs_exact_matching(self):
        """
        Exact genre match scores higher than fuzzy match,
        but fuzzy match scores higher than no genre match.

        This is the key property: exact > fuzzy > zero
        """
        weight = 2.3

        # Exact match
        exact_score = weight * genre_similarity("pop", "pop")

        # Fuzzy match
        fuzzy_score = weight * genre_similarity("pop", "synth-pop")

        # No match
        zero_score = weight * genre_similarity("pop", "metal")

        self.assertGreater(exact_score, fuzzy_score,
                          f"Exact should score higher: {exact_score} > {fuzzy_score}")
        self.assertGreater(fuzzy_score, zero_score,
                          f"Fuzzy should score higher than zero: {fuzzy_score} > {zero_score}")


if __name__ == '__main__':
    unittest.main()
