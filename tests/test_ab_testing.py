"""Tests for A/B testing framework."""

import unittest
from src.ab_testing import ABTester, ABTestResult, MultiUserABTester
from src.recommender import Song


class TestABTester(unittest.TestCase):
    """Test A/B testing functionality."""

    def setUp(self):
        """Create test songs."""
        self.songs_original = [
            Song(1, "Song A", "Artist A", "pop", "happy", 0.8, 120, 0.8, 0.7, 0.2, 70, "2020s", "", 0.7, 0.8),
            Song(2, "Song B", "Artist B", "rock", "intense", 0.9, 140, 0.6, 0.8, 0.1, 65, "2020s", "", 0.6, 0.8),
            Song(3, "Song C", "Artist C", "pop", "happy", 0.85, 125, 0.75, 0.75, 0.2, 68, "2020s", "", 0.7, 0.8),
            Song(4, "Song D", "Artist D", "electronic", "calm", 0.3, 100, 0.5, 0.4, 0.8, 60, "2020s", "", 0.5, 0.7),
            Song(5, "Song E", "Artist E", "rock", "intense", 0.88, 135, 0.65, 0.8, 0.1, 62, "2020s", "", 0.6, 0.8),
        ]

        self.songs_learned = [
            Song(1, "Song A", "Artist A", "pop", "happy", 0.8, 120, 0.8, 0.7, 0.2, 72, "2020s", "", 0.7, 0.8),
            Song(2, "Song B", "Artist B", "rock", "intense", 0.9, 140, 0.6, 0.8, 0.1, 68, "2020s", "", 0.6, 0.8),
            Song(6, "Song F", "Artist F", "lofi", "calm", 0.2, 95, 0.55, 0.3, 0.85, 55, "2020s", "", 0.5, 0.8),
            Song(7, "Song G", "Artist G", "electronic", "calm", 0.25, 98, 0.5, 0.35, 0.9, 58, "2020s", "", 0.5, 0.7),
            Song(8, "Song H", "Artist H", "indie", "nostalgic", 0.5, 110, 0.6, 0.55, 0.6, 61, "2020s", "", 0.6, 0.8),
        ]

        self.original_scores = [8.5, 8.2, 8.3, 7.5, 8.1]
        self.learned_scores = [8.6, 8.3, 7.9, 7.8, 8.0]

    def test_compare_recommendations(self):
        """Test comparing two recommendation sets."""
        result = ABTester.compare_recommendations(
            self.songs_original,
            self.songs_learned,
            self.original_scores,
            self.learned_scores,
        )

        self.assertEqual(result.overlap_count, 2)  # Songs A and B
        self.assertAlmostEqual(result.overlap_percentage, 40.0)
        self.assertEqual(result.unique_in_original, 3)
        self.assertEqual(result.unique_in_learned, 3)

    def test_overlap_calculation(self):
        """Test overlap percentage calculation."""
        result = ABTester.compare_recommendations(
            self.songs_original,
            self.songs_learned,
            self.original_scores,
            self.learned_scores,
        )

        # 2 out of 5 = 40%
        self.assertAlmostEqual(result.overlap_percentage, 40.0)

    def test_score_improvement(self):
        """Test score improvement calculation."""
        result = ABTester.compare_recommendations(
            self.songs_original,
            self.songs_learned,
            self.original_scores,
            self.learned_scores,
        )

        original_avg = sum(self.original_scores) / len(self.original_scores)
        learned_avg = sum(self.learned_scores) / len(self.learned_scores)

        expected_improvement = ((learned_avg - original_avg) / original_avg) * 100

        self.assertAlmostEqual(result.score_improvement, expected_improvement, places=1)

    def test_diversity_score(self):
        """Test diversity score calculation."""
        diversity = ABTester.calculate_diversity_score(self.songs_original)

        # Should be between 0 and 1
        self.assertGreater(diversity, 0.0)
        self.assertLess(diversity, 1.0)

    def test_quality_metrics(self):
        """Test quality metrics calculation."""
        metrics = ABTester.calculate_quality_metrics(self.songs_original, self.original_scores)

        self.assertIn("avg_score", metrics)
        self.assertIn("max_score", metrics)
        self.assertIn("min_score", metrics)
        self.assertIn("std_dev", metrics)
        self.assertIn("diversity", metrics)

        self.assertEqual(metrics["max_score"], max(self.original_scores))
        self.assertEqual(metrics["min_score"], min(self.original_scores))

    def test_format_comparison_report(self):
        """Test report formatting."""
        result = ABTester.compare_recommendations(
            self.songs_original,
            self.songs_learned,
            self.original_scores,
            self.learned_scores,
        )

        report = ABTester.format_comparison_report(result)

        self.assertIn("A/B TEST RESULTS", report)
        self.assertIn("OVERLAP", report)
        self.assertIn("SCORE IMPROVEMENT", report)
        self.assertIn("Improvement:", report)


class TestMultiUserABTester(unittest.TestCase):
    """Test multi-user A/B testing."""

    def setUp(self):
        """Create test results."""
        self.tester = MultiUserABTester()

        # Create 3 test results with different outcomes
        songs = [
            Song(i, f"Song {i}", f"Artist {i}", "pop", "happy", 0.8, 120, 0.8, 0.7, 0.2, 70, "2020s", "", 0.7, 0.8)
            for i in range(1, 6)
        ]

        # User 1: 20% improvement
        result1 = ABTestResult(
            original_songs=songs[:3],
            learned_songs=songs[:3],
            overlap_count=3,
            overlap_percentage=100.0,
            original_avg_score=8.0,
            learned_avg_score=8.2,  # +2.5%
            score_improvement=2.5,
            unique_in_original=0,
            unique_in_learned=0,
        )

        # User 2: no improvement
        result2 = ABTestResult(
            original_songs=songs[:3],
            learned_songs=songs[2:5],
            overlap_count=1,
            overlap_percentage=33.3,
            original_avg_score=8.0,
            learned_avg_score=8.0,  # +0%
            score_improvement=0.0,
            unique_in_original=2,
            unique_in_learned=2,
        )

        # User 3: 10% improvement
        result3 = ABTestResult(
            original_songs=songs[:3],
            learned_songs=songs[:3],
            overlap_count=3,
            overlap_percentage=100.0,
            original_avg_score=7.5,
            learned_avg_score=8.25,  # +10%
            score_improvement=10.0,
            unique_in_original=0,
            unique_in_learned=0,
        )

        self.tester.add_result(result1)
        self.tester.add_result(result2)
        self.tester.add_result(result3)

    def test_aggregate_metrics(self):
        """Test aggregation across users."""
        metrics = self.tester.aggregate_metrics()

        self.assertEqual(metrics["num_users"], 3)
        self.assertIn("avg_overlap", metrics)
        self.assertIn("avg_improvement", metrics)
        self.assertIn("improvement_rate", metrics)

    def test_improvement_rate_calculation(self):
        """Test improvement rate calculation."""
        metrics = self.tester.aggregate_metrics()

        # 2 out of 3 users saw improvement (66.7%)
        self.assertAlmostEqual(metrics["improvement_rate"], 66.67, places=1)

    def test_format_summary(self):
        """Test summary formatting."""
        summary = self.tester.format_summary()

        self.assertIn("MULTI-USER A/B TEST SUMMARY", summary)
        self.assertIn("Users Tested:", summary)
        self.assertIn("Improvement", summary)


if __name__ == "__main__":
    unittest.main()
