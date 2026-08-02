"""
A/B Testing Framework — Compare original vs learned recommendations.

Enables:
- Side-by-side comparison of recommendations
- Quality metrics (overlap, score differences)
- Statistical analysis of learning impact
- Visual comparison reports
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from .recommender import Song
import math


@dataclass
class ABTestResult:
    """Result of A/B comparison between original and learned."""

    original_songs: List[Song]
    learned_songs: List[Song]
    overlap_count: int  # Songs in both lists
    overlap_percentage: float  # overlap_count / k * 100
    original_avg_score: float
    learned_avg_score: float
    score_improvement: float  # (learned - original) / original * 100
    unique_in_original: int  # Songs only in original
    unique_in_learned: int  # Songs only in learned


class ABTester:
    """Framework for A/B testing original vs learned embeddings."""

    @staticmethod
    def compare_recommendations(
        original: List[Song],
        learned: List[Song],
        original_scores: List[float],
        learned_scores: List[float],
    ) -> ABTestResult:
        """
        Compare two sets of recommendations.

        Args:
            original: Baseline recommendations
            learned: Recommendations with learned embeddings
            original_scores: Scores for original recommendations
            learned_scores: Scores for learned recommendations

        Returns:
            ABTestResult with comparison metrics
        """
        # Calculate overlap
        original_ids = {song.id for song in original}
        learned_ids = {song.id for song in learned}
        overlap_ids = original_ids & learned_ids

        overlap_count = len(overlap_ids)
        overlap_percentage = (overlap_count / len(original) * 100) if original else 0

        # Calculate score improvements
        original_avg = sum(original_scores) / len(original_scores) if original_scores else 0
        learned_avg = sum(learned_scores) / len(learned_scores) if learned_scores else 0

        if original_avg > 0:
            score_improvement = ((learned_avg - original_avg) / original_avg) * 100
        else:
            score_improvement = 0

        # Count unique
        unique_original = len(original_ids - learned_ids)
        unique_learned = len(learned_ids - original_ids)

        return ABTestResult(
            original_songs=original,
            learned_songs=learned,
            overlap_count=overlap_count,
            overlap_percentage=overlap_percentage,
            original_avg_score=original_avg,
            learned_avg_score=learned_avg,
            score_improvement=score_improvement,
            unique_in_original=unique_original,
            unique_in_learned=unique_learned,
        )

    @staticmethod
    def calculate_diversity_score(songs: List[Song]) -> float:
        """
        Calculate diversity score based on genre/artist distribution.

        Args:
            songs: List of songs

        Returns:
            Diversity score (0.0-1.0, higher = more diverse)
        """
        if not songs:
            return 0.0

        genres = [song.genre for song in songs]
        artists = [song.artist for song in songs]

        # Unique count normalized by total count
        genre_diversity = len(set(genres)) / len(genres)
        artist_diversity = len(set(artists)) / len(artists)

        # Weighted average
        return (genre_diversity * 0.6 + artist_diversity * 0.4)

    @staticmethod
    def calculate_quality_metrics(songs: List[Song], scores: List[float]) -> Dict:
        """
        Calculate quality metrics for recommendations.

        Args:
            songs: List of songs
            scores: Scores for each song

        Returns:
            Dict with metrics
        """
        if not songs or not scores:
            return {}

        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)

        # Standard deviation (consistency)
        if len(scores) > 1:
            variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0

        # Genre/artist concentration
        genres = [song.genre for song in songs]
        artists = [song.artist for song in songs]
        genre_concentration = len(set(genres)) / len(genres)  # Lower = more concentration
        artist_concentration = len(set(artists)) / len(artists)

        return {
            "avg_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "std_dev": std_dev,
            "diversity": ABTester.calculate_diversity_score(songs),
            "genre_concentration": genre_concentration,
            "artist_concentration": artist_concentration,
        }

    @staticmethod
    def format_comparison_report(result: ABTestResult) -> str:
        """
        Format A/B test result as readable report.

        Args:
            result: ABTestResult from compare_recommendations

        Returns:
            Formatted report string
        """
        original_metrics = ABTester.calculate_quality_metrics(
            result.original_songs, [float(s.popularity) for s in result.original_songs]
        )
        learned_metrics = ABTester.calculate_quality_metrics(
            result.learned_songs, [float(s.popularity) for s in result.learned_songs]
        )

        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║                  A/B TEST RESULTS
╚═══════════════════════════════════════════════════════════════╝

📊 OVERLAP & CHANGES
  Overlap:        {result.overlap_count}/5 songs ({result.overlap_percentage:.0f}%)
  Only Original:  {result.unique_in_original} songs
  Only Learned:   {result.unique_in_learned} songs

📈 SCORE IMPROVEMENT
  Original Avg:   {result.original_avg_score:.2f}
  Learned Avg:    {result.learned_avg_score:.2f}
  Improvement:    {result.score_improvement:+.1f}%

🎵 ORIGINAL RECOMMENDATIONS
  Diversity:      {original_metrics.get('diversity', 0):.2f}
  Avg Score:      {original_metrics.get('avg_score', 0):.2f}
  Consistency:    {original_metrics.get('std_dev', 0):.3f} (σ)

🧠 LEARNED RECOMMENDATIONS
  Diversity:      {learned_metrics.get('diversity', 0):.2f}
  Avg Score:      {learned_metrics.get('avg_score', 0):.2f}
  Consistency:    {learned_metrics.get('std_dev', 0):.3f} (σ)

🎸 ARTIST DIVERSITY
  Original:       {len(set(s.artist for s in result.original_songs))}/5
  Learned:        {len(set(s.artist for s in result.learned_songs))}/5

🎭 GENRE DIVERSITY
  Original:       {len(set(s.genre for s in result.original_songs))}/5
  Learned:        {len(set(s.genre for s in result.learned_songs))}/5

═══════════════════════════════════════════════════════════════
"""
        return report


class MultiUserABTester:
    """
    A/B testing across multiple users.

    Enables statistical analysis of learning impact across user base.
    """

    def __init__(self):
        self.results = []

    def add_result(self, result: ABTestResult) -> None:
        """Add A/B test result."""
        self.results.append(result)

    def aggregate_metrics(self) -> Dict:
        """
        Calculate aggregate metrics across all test results.

        Returns:
            Dict with average metrics
        """
        if not self.results:
            return {}

        avg_overlap = sum(r.overlap_percentage for r in self.results) / len(self.results)
        avg_improvement = sum(r.score_improvement for r in self.results) / len(self.results)
        avg_original_score = sum(r.original_avg_score for r in self.results) / len(self.results)
        avg_learned_score = sum(r.learned_avg_score for r in self.results) / len(self.results)

        # Count how many users saw improvement
        improved_count = sum(1 for r in self.results if r.score_improvement > 0)
        improvement_rate = (improved_count / len(self.results) * 100) if self.results else 0

        return {
            "num_users": len(self.results),
            "avg_overlap": avg_overlap,
            "avg_improvement": avg_improvement,
            "improvement_rate": improvement_rate,
            "avg_original_score": avg_original_score,
            "avg_learned_score": avg_learned_score,
        }

    def format_summary(self) -> str:
        """Format summary report for all users."""
        metrics = self.aggregate_metrics()

        if not metrics:
            return "No test results available"

        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║           MULTI-USER A/B TEST SUMMARY
╚═══════════════════════════════════════════════════════════════╝

📊 AGGREGATE RESULTS
  Users Tested:           {metrics['num_users']}
  Avg Recommendation Overlap: {metrics['avg_overlap']:.1f}%
  Users with Improvement: {metrics['improvement_rate']:.0f}%

📈 SCORE METRICS
  Avg Original Score:     {metrics['avg_original_score']:.2f}
  Avg Learned Score:      {metrics['avg_learned_score']:.2f}
  Avg Improvement:        {metrics['avg_improvement']:+.1f}%

✅ INTERPRETATION
"""
        if metrics['improvement_rate'] >= 80:
            summary += "  🌟 STRONG LEARNING — System improved for most users\n"
        elif metrics['improvement_rate'] >= 50:
            summary += "  ✓ MODERATE LEARNING — System improved for ~half of users\n"
        else:
            summary += "  ⚠️  WEAK LEARNING — Limited improvement, feedback may need tuning\n"

        summary += "═══════════════════════════════════════════════════════════════\n"
        return summary
