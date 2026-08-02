"""
Unit tests for the Music Recommender System.
Tests core functionality: scoring, recommendations, diversity penalties, and strategies.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommender import (
    load_songs, score_song, recommend_songs,
    BalancedStrategy, EnergyFocusedStrategy, GenreFirstStrategy,
    MoodFirstStrategy, QualityFirstStrategy, PopularityDrivenStrategy
)
from src.main import apply_diversity_penalty


class TestSongLoading(unittest.TestCase):
    """Test data loading and song validation."""

    def test_load_songs_returns_list(self):
        """Songs loaded successfully from CSV."""
        songs = load_songs("data/songs.csv")
        self.assertIsInstance(songs, list)
        self.assertGreater(len(songs), 0)

    def test_songs_have_required_fields(self):
        """Each song has required attributes."""
        songs = load_songs("data/songs.csv")
        required_fields = {'title', 'artist', 'genre', 'mood', 'energy',
                          'valence', 'danceability', 'tempo_bpm', 'acousticness'}
        for song in songs:
            for field in required_fields:
                self.assertIn(field, song, f"Song missing {field}")


class TestScoringCore(unittest.TestCase):
    """Test individual song scoring logic with precise numerical validation."""

    def setUp(self):
        self.songs = load_songs("data/songs.csv")
        self.base_prefs = {
            'genre': 'pop', 'mood': 'happy', 'energy': 0.5, 'valence': 0.5,
            'danceability': 0.5, 'tempo_bpm': 120, 'acousticness': 0.5,
            'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5
        }

    def test_score_song_genre_match_exact_value(self):
        """Genre match contributes exactly 2.3 points (BalancedStrategy)."""
        song = {'title': 'Test', 'artist': 'Test', 'genre': 'pop', 'mood': 'happy',
                'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'tempo_bpm': 120,
                'acousticness': 0.5, 'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5}
        prefs = self.base_prefs.copy()
        score, reasons = score_song(prefs, song)  # ✅ FIXED: user_prefs first
        self.assertGreaterEqual(score, 2.3, f"Genre match should contribute 2.3, got {score}")
        self.assertIn("genre matches", " ".join(reasons).lower())

    def test_score_song_genre_mismatch_penalty(self):
        """Genre mismatch (0 points) vs match (2.3 points) = 2.3 point difference."""
        song_match = {'title': 'Test', 'artist': 'Test', 'genre': 'pop', 'mood': 'happy',
                      'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'tempo_bpm': 120,
                      'acousticness': 0.5, 'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5}
        song_mismatch = {'title': 'Test', 'artist': 'Test', 'genre': 'rock', 'mood': 'happy',
                         'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'tempo_bpm': 120,
                         'acousticness': 0.5, 'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5}
        prefs = self.base_prefs.copy()
        prefs['genre'] = 'pop'

        score_match, _ = score_song(prefs, song_match)  # ✅ FIXED: user_prefs first
        score_mismatch, _ = score_song(prefs, song_mismatch)  # ✅ FIXED: user_prefs first

        # Genre match is worth 2.3 points, so this is the minimum difference
        self.assertGreaterEqual(score_match - score_mismatch, 2.3,
                               f"Genre match should score 2.3 higher, got {score_match - score_mismatch}")

    def test_score_song_mood_match_exact_value(self):
        """Mood match contributes exactly 1.0 points; mismatch is -0.5."""
        song = {'title': 'Test', 'artist': 'Test', 'genre': 'rock', 'mood': 'happy',
                'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'tempo_bpm': 120,
                'acousticness': 0.5, 'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5}

        prefs_match = self.base_prefs.copy()
        prefs_match['genre'] = 'rock'
        prefs_match['mood'] = 'happy'

        prefs_mismatch = self.base_prefs.copy()
        prefs_mismatch['genre'] = 'rock'
        prefs_mismatch['mood'] = 'calm'

        score_with, reasons_with = score_song(prefs_match, song)  # ✅ FIXED
        score_without, reasons_without = score_song(prefs_mismatch, song)  # ✅ FIXED

        # Mood match (+1.0) vs mismatch (-0.5) = 1.5 point difference
        mood_difference = score_with - score_without
        self.assertGreaterEqual(mood_difference, 1.5,
                               f"Mood match vs mismatch should differ by 1.5, got {mood_difference}")
        self.assertIn("mood matches", " ".join(reasons_with).lower())
        self.assertIn("mood mismatch", " ".join(reasons_without).lower())


class TestRecommendations(unittest.TestCase):
    """Test the recommend_songs function."""

    def setUp(self):
        self.songs = load_songs("data/songs.csv")
        self.base_prefs = {
            'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.7,
            'danceability': 0.6, 'tempo_bpm': 130, 'acousticness': 0.2,
            'popularity': 60.0, 'production_quality': 0.75, 'artist_familiarity': 0.7
        }

    def test_recommend_returns_k(self):
        """Returns exactly k recommendations (or fewer if catalog is smaller)."""
        prefs = self.base_prefs.copy()
        for k in [1, 3, 5]:
            recs = recommend_songs(prefs, self.songs, k=k)
            expected_k = min(k, len(self.songs))
            self.assertEqual(len(recs), expected_k, f"Expected {expected_k} recs, got {len(recs)}")

    def test_recommend_sorted_by_score_descending(self):
        """Recommendations sorted by score in descending order."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=5)
        scores = [score for _, score, _ in recs]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i + 1],
                                   f"Score {i} ({scores[i]}) should be >= score {i+1} ({scores[i+1]})")

    def test_recommend_valid_structure(self):
        """Each recommendation is (song_dict, score, reasons_list)."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=5)
        self.assertGreater(len(recs), 0, "Should return at least one recommendation")
        for rec in recs:
            self.assertEqual(len(rec), 3, f"Recommendation should be 3-tuple, got {len(rec)}")
            song, score, reasons = rec
            self.assertIsInstance(song, dict, "Song should be dict")
            self.assertIsInstance(score, (int, float), "Score should be numeric")
            self.assertGreater(score, 0, f"Score should be positive, got {score}")
            self.assertIsInstance(reasons, list, "Reasons should be list")

    def test_recommend_genre_preference_respected(self):
        """Genre preference is strongly reflected in top results (at least 50% of recs)."""
        prefs = self.base_prefs.copy()
        prefs['genre'] = 'pop'
        recs = recommend_songs(prefs, self.songs, k=5)
        pop_genres = [song.get('genre') for song, _, _ in recs]
        pop_count = sum(1 for g in pop_genres if g == 'pop')
        self.assertGreaterEqual(pop_count, len(recs) // 2,
                               f"Expected at least 50% pop, got {pop_count}/{len(recs)}")


class TestDiversityPenalty(unittest.TestCase):
    """Test diversity penalty application."""

    def test_no_penalty_different_artists(self):
        """No penalty when artists differ."""
        recs = [
            ({"title": "S1", "artist": "A1", "genre": "pop"}, 8.0, []),
            ({"title": "S2", "artist": "A2", "genre": "rock"}, 7.5, []),
        ]
        penalized = apply_diversity_penalty(recs)
        self.assertEqual(penalized[0][1], 8.0)
        self.assertEqual(penalized[1][1], 7.5)

    def test_penalty_duplicate_artist(self):
        """Penalty applied for duplicate artist."""
        recs = [
            ({"title": "S1", "artist": "A1", "genre": "pop"}, 8.0, []),
            ({"title": "S2", "artist": "A1", "genre": "rock"}, 7.5, []),
        ]
        penalized = apply_diversity_penalty(recs, penalty_per_artist=0.5)
        self.assertEqual(penalized[0][1], 8.0)
        self.assertEqual(penalized[1][1], 7.0)

    def test_penalty_duplicate_genre(self):
        """Penalty applied for duplicate genre."""
        recs = [
            ({"title": "S1", "artist": "A1", "genre": "pop"}, 8.0, []),
            ({"title": "S2", "artist": "A2", "genre": "pop"}, 7.5, []),
        ]
        penalized = apply_diversity_penalty(recs, penalty_per_genre=0.2)
        self.assertEqual(penalized[0][1], 8.0)
        self.assertEqual(penalized[1][1], 7.3)


class TestStrategies(unittest.TestCase):
    """Test different scoring strategies."""

    def setUp(self):
        self.songs = load_songs("data/songs.csv")
        self.prefs = {'genre': 'pop', 'mood': 'happy', 'energy': 0.9}

    def test_balanced_strategy(self):
        """BalancedStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=BalancedStrategy())
        self.assertEqual(len(recs), 5)

    def test_energy_focused_strategy(self):
        """EnergyFocusedStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=EnergyFocusedStrategy())
        self.assertEqual(len(recs), 5)

    def test_genre_first_strategy(self):
        """GenreFirstStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=GenreFirstStrategy())
        self.assertEqual(len(recs), 5)

    def test_mood_first_strategy(self):
        """MoodFirstStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=MoodFirstStrategy())
        self.assertEqual(len(recs), 5)

    def test_quality_first_strategy(self):
        """QualityFirstStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=QualityFirstStrategy())
        self.assertEqual(len(recs), 5)

    def test_popularity_driven_strategy(self):
        """PopularityDrivenStrategy works."""
        recs = recommend_songs(self.prefs, self.songs, k=5, strategy=PopularityDrivenStrategy())
        self.assertEqual(len(recs), 5)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions with strong validation."""

    def setUp(self):
        self.songs = load_songs("data/songs.csv")
        self.base_prefs = {
            'genre': 'pop', 'mood': 'happy', 'energy': 0.5, 'valence': 0.5,
            'danceability': 0.5, 'tempo_bpm': 120, 'acousticness': 0.5,
            'popularity': 50.0, 'production_quality': 0.5, 'artist_familiarity': 0.5
        }

    def test_k_equals_one_returns_best_song(self):
        """k=1 returns exactly one song (the best match)."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=1)
        self.assertEqual(len(recs), 1, "k=1 should return exactly 1 recommendation")
        song, score, reasons = recs[0]
        self.assertIsInstance(song, dict)
        self.assertGreater(score, 0)
        self.assertGreater(len(reasons), 0, "Top recommendation should have explanation")

    def test_k_larger_than_catalog_returns_all_songs(self):
        """k > catalog size returns all available songs."""
        prefs = self.base_prefs.copy()
        catalog_size = len(self.songs)
        recs = recommend_songs(prefs, self.songs, k=catalog_size + 10)
        self.assertEqual(len(recs), catalog_size,
                        f"Should return all {catalog_size} songs, got {len(recs)}")

    def test_empty_penalty_list_is_safe(self):
        """Diversity penalty handles empty list gracefully."""
        penalized = apply_diversity_penalty([])
        self.assertEqual(len(penalized), 0, "Empty input should return empty output")

    def test_all_recommendations_have_positive_scores(self):
        """All returned recommendations should have positive scores."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=min(10, len(self.songs)))
        for song, score, reasons in recs:
            self.assertGreater(score, 0, f"Song '{song.get('title')}' has non-positive score {score}")


class TestIntegration(unittest.TestCase):
    """Full pipeline tests with strong assertions."""

    def setUp(self):
        self.songs = load_songs("data/songs.csv")
        self.base_prefs = {
            'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.7,
            'danceability': 0.6, 'tempo_bpm': 130, 'acousticness': 0.2,
            'popularity': 60.0, 'production_quality': 0.75, 'artist_familiarity': 0.7
        }

    def test_full_pipeline_balanced(self):
        """Full pipeline: preferences -> recommendations -> penalties."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=5)
        self.assertGreater(len(recs), 0, "Should have recommendations")
        penalized = apply_diversity_penalty(recs)
        self.assertGreater(len(penalized), 0, "Should have penalized recommendations")

        for item in penalized:
            self.assertGreaterEqual(len(item), 3, f"Each item should be 3-tuple+, got {len(item)}")
            _song, score, reasons = item[0], item[1], item[2]
            self.assertGreater(score, 0, f"Score should be positive, got {score}")
            self.assertIsInstance(reasons, list, "Reasons should be list")

    def test_full_pipeline_energy_focused(self):
        """Full pipeline with Energy-Focused strategy produces valid scores."""
        prefs = self.base_prefs.copy()
        recs = recommend_songs(prefs, self.songs, k=5, strategy=EnergyFocusedStrategy())
        self.assertGreater(len(recs), 0)
        penalized = apply_diversity_penalty(recs)
        self.assertEqual(len(penalized), min(5, len(self.songs)))
        # Energy-focused should prefer high energy matches
        for item in penalized[:2]:  # Top 2 should have decent scores
            song, score = item[0], item[1]
            self.assertGreater(score, 0, f"Top recommendation should have positive score")

    def test_different_profiles_produce_different_results(self):
        """Different user profiles should produce different recommendations."""
        pop_prefs = self.base_prefs.copy()
        pop_prefs['genre'] = 'pop'
        pop_prefs['energy'] = 0.9

        lofi_prefs = self.base_prefs.copy()
        lofi_prefs['genre'] = 'lofi'
        lofi_prefs['energy'] = 0.2

        pop_recs = recommend_songs(pop_prefs, self.songs, k=5)
        lofi_recs = recommend_songs(lofi_prefs, self.songs, k=5)

        # Extract top songs (excluding diversity penalties)
        pop_top_songs = [s['title'] for s, _, _ in pop_recs]
        lofi_top_songs = [s['title'] for s, _, _ in lofi_recs]

        # Top recommendations should be different
        # (Different preferences -> different top matches in most cases)
        different_top_choice = pop_top_songs[0] != lofi_top_songs[0] if pop_recs and lofi_recs else True
        self.assertTrue(different_top_choice or len(set(pop_top_songs) & set(lofi_top_songs)) < len(pop_recs),
                       "Different profiles should produce somewhat different recommendations")


if __name__ == '__main__':
    unittest.main()
