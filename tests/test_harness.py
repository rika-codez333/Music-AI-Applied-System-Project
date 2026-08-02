"""
Test Harness & Evaluation Script

Runs predefined test cases and produces structured evaluation reports
with pass/fail metrics, confidence scores, and performance summaries.

Usage:
    python tests/test_harness.py

Output: Structured evaluation report with:
    - Pass/fail status for each test
    - Confidence scores (0.0-1.0)
    - Component summaries
    - Overall system score
"""

import sys
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json

# Add src to path
sys.path.insert(0, '/Users/rikaraxkz/Desktop/CodePath/AI110/Music-AI-Applied-System-Project')

from src.recommender import Recommender, UserProfile, Song, load_songs
from src.feedback import FeedbackAnalyzer
from src.learner import EmbeddingLearner, FeedbackValidator, FeedbackMemory
from src.feedback_loop import FeedbackLoop


@dataclass
class TestResult:
    """Result of a single test case."""
    test_name: str
    test_category: str
    passed: bool
    confidence: float  # 0.0-1.0, how confident in the result
    message: str
    details: Dict = None

    def to_dict(self):
        return {
            'test_name': self.test_name,
            'category': self.test_category,
            'passed': self.passed,
            'confidence': round(self.confidence, 2),
            'message': self.message,
            'details': self.details or {}
        }


class EvaluationHarness:
    """Runs predefined test cases and produces evaluation report."""

    def __init__(self):
        songs_dicts = load_songs('data/songs.csv')
        # Convert dicts to Song objects
        songs = [Song(**s) for s in songs_dicts]
        self.recommender = Recommender(songs)
        self.learner = EmbeddingLearner()
        self.analyzer = FeedbackAnalyzer()
        self.loop = FeedbackLoop(self.recommender, self.learner)
        self.results: List[TestResult] = []

    def run_all_tests(self) -> Dict:
        """Run all test categories and return results."""
        print("=" * 80)
        print("🧪 MUSIC AI RECOMMENDER — TEST HARNESS")
        print("=" * 80)
        print()

        self._test_core_recommender()
        self._test_semantic_similarity()
        self._test_feedback_parsing()
        self._test_feedback_loop()
        self._test_learning_gates()

        return self._generate_report()

    def _test_core_recommender(self):
        """Test core recommendation functionality."""
        print("📊 Testing Core Recommender...")

        user = UserProfile(
            favorite_genre='pop',
            favorite_mood='happy',
            target_energy=0.8,
            preferred_valence=0.85,
            preferred_danceability=0.75,
            preferred_tempo_bpm=130,
            preferred_acousticness=0.3,
            min_popularity=50,
            preferred_production_quality=0.7,
            prefer_artist_familiarity=True
        )

        recs = self.recommender.recommend(user, k=5)

        # Test 1: Recommendations returned
        passed = len(recs) == 5
        confidence = 1.0 if passed else 0.0
        self.results.append(TestResult(
            test_name='Recommendations Generated (k=5)',
            test_category='Core Recommender',
            passed=passed,
            confidence=confidence,
            message='5 recommendations returned' if passed else 'Wrong number of recommendations',
            details={'count': len(recs), 'expected': 5}
        ))

        # Test 2: All songs have valid attributes
        all_valid = all(hasattr(s, 'title') and hasattr(s, 'artist') and hasattr(s, 'genre') for s in recs)
        confidence = 1.0 if all_valid else 0.7
        self.results.append(TestResult(
            test_name='Song Attributes Valid',
            test_category='Core Recommender',
            passed=all_valid,
            confidence=confidence,
            message=f'All songs have valid attributes',
            details={'sample_titles': [s.title for s in recs[:3]]}
        ))

        # Test 3: No duplicate recommendations
        titles = [s.title for s in recs]
        no_dupes = len(titles) == len(set(titles))
        confidence = 1.0 if no_dupes else 0.0
        self.results.append(TestResult(
            test_name='No Duplicate Recommendations',
            test_category='Core Recommender',
            passed=no_dupes,
            confidence=confidence,
            message='No duplicate songs in recommendations',
            details={'total': len(recs), 'unique': len(set(titles))}
        ))

    def _test_semantic_similarity(self):
        """Test semantic genre and mood similarity."""
        print("🎯 Testing Semantic Similarity...")

        from src.recommender import genre_similarity, mood_similarity

        # Test 1: Exact genre match
        similarity = genre_similarity('pop', 'pop')
        passed = abs(similarity - 1.0) < 0.01
        self.results.append(TestResult(
            test_name='Genre: Exact Match (pop ↔ pop)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=1.0,
            message=f'Similarity: {similarity}',
            details={'result': round(similarity, 2), 'expected': 1.0}
        ))

        # Test 2: Related genres
        similarity = genre_similarity('synthwave', 'electronic')
        passed = 0.7 <= similarity <= 0.8  # Expect ~0.75
        confidence = 0.95 if passed else 0.6
        self.results.append(TestResult(
            test_name='Genre: Related Pair (synthwave ↔ electronic)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=confidence,
            message=f'Similarity: {round(similarity, 2)} (expected ~0.75)',
            details={'result': round(similarity, 2), 'expected_range': '0.70-0.80'}
        ))

        # Test 3: Unrelated genres
        similarity = genre_similarity('jazz', 'hip-hop')
        passed = similarity < 0.3
        confidence = 0.9 if passed else 0.6
        self.results.append(TestResult(
            test_name='Genre: Unrelated Pair (jazz ↔ hip-hop)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=confidence,
            message=f'Similarity: {round(similarity, 2)} (expected <0.3)',
            details={'result': round(similarity, 2), 'expected_max': 0.3}
        ))

        # Test 4: Exact mood match
        similarity = mood_similarity('calm', 'calm')
        passed = abs(similarity - 1.0) < 0.01
        self.results.append(TestResult(
            test_name='Mood: Exact Match (calm ↔ calm)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=1.0,
            message=f'Similarity: {similarity}',
            details={'result': round(similarity, 2), 'expected': 1.0}
        ))

        # Test 5: Similar moods
        similarity = mood_similarity('calm', 'chill')
        passed = 0.9 <= similarity <= 1.0
        confidence = 0.95 if passed else 0.7
        self.results.append(TestResult(
            test_name='Mood: Similar Pair (calm ↔ chill)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=confidence,
            message=f'Similarity: {round(similarity, 2)} (expected ~0.95)',
            details={'result': round(similarity, 2), 'expected_range': '0.90-1.00'}
        ))

        # Test 6: Opposite moods
        similarity = mood_similarity('happy', 'sad')
        passed = similarity < 0.5
        confidence = 0.9 if passed else 0.6
        self.results.append(TestResult(
            test_name='Mood: Opposite Pair (happy ↔ sad)',
            test_category='Semantic Similarity',
            passed=passed,
            confidence=confidence,
            message=f'Similarity: {round(similarity, 2)} (expected <0.5)',
            details={'result': round(similarity, 2), 'expected_max': 0.5}
        ))

    def _test_feedback_parsing(self):
        """Test feedback intent parsing."""
        print("💬 Testing Feedback Parsing...")

        test_cases = [
            ("I liked that but it was too energetic", 'energy_lower', 0.80),
            ("I want something more relaxing", 'energy_lower', 0.75),
            ("Make it louder and more intense", 'energy_higher', 0.85),
            ("I'd prefer a calmer mood", 'mood_shift', 0.70),
            ("That was perfect!", 'positive_validation', 0.90),
            ("eh whatever", 'unknown', 0.30),  # Ambiguous
        ]

        for feedback, expected_type, min_confidence in test_cases:
            intent = self.analyzer.parse(feedback)
            confidence_check = intent.confidence >= min_confidence - 0.1  # Allow ±10%
            passed = confidence_check

            self.results.append(TestResult(
                test_name=f'Parse: "{feedback[:40]}"',
                test_category='Feedback Parsing',
                passed=passed,
                confidence=0.9 if passed else 0.5,
                message=f'Type: {intent.adjustment_type}, Confidence: {round(intent.confidence, 2)}',
                details={
                    'feedback': feedback,
                    'type_detected': str(intent.adjustment_type),
                    'confidence': round(intent.confidence, 2),
                    'min_expected': min_confidence
                }
            ))

    def _test_feedback_loop(self):
        """Test complete feedback loop."""
        print("🔄 Testing Feedback Loop...")

        user = UserProfile(
            favorite_genre='pop',
            favorite_mood='happy',
            target_energy=0.85,
            preferred_valence=0.8,
            preferred_danceability=0.75,
            preferred_tempo_bpm=130,
            preferred_acousticness=0.3,
            min_popularity=50,
            preferred_production_quality=0.7,
            prefer_artist_familiarity=True
        )

        feedback = "I liked that but I want something calmer"
        result = self.loop.process_feedback(user, feedback, k=5)

        # Test 1: Original recommendations generated
        passed = len(result.original_recommendations) == 5
        self.results.append(TestResult(
            test_name='Loop: Original Recommendations Generated',
            test_category='Feedback Loop',
            passed=passed,
            confidence=1.0 if passed else 0.5,
            message='5 original recommendations generated',
            details={'count': len(result.original_recommendations)}
        ))

        # Test 2: Adjusted recommendations generated
        passed = len(result.adjusted_recommendations) == 5
        self.results.append(TestResult(
            test_name='Loop: Adjusted Recommendations Generated',
            test_category='Feedback Loop',
            passed=passed,
            confidence=1.0 if passed else 0.5,
            message='5 adjusted recommendations generated',
            details={'count': len(result.adjusted_recommendations)}
        ))

        # Test 3: Intent extracted
        passed = result.feedback_intent.adjustment_type is not None
        self.results.append(TestResult(
            test_name='Loop: Intent Extracted',
            test_category='Feedback Loop',
            passed=passed,
            confidence=0.95 if passed else 0.5,
            message=f'Intent: {result.feedback_intent.adjustment_type}',
            details={'intent': str(result.feedback_intent.adjustment_type)}
        ))

        # Test 4: Validation performed
        passed = result.validation_passed is not None
        self.results.append(TestResult(
            test_name='Loop: Validation Executed',
            test_category='Feedback Loop',
            passed=passed,
            confidence=1.0 if passed else 0.0,
            message=f'Validation: {result.validation_passed}, Confidence: {round(result.validation_confidence, 2)}',
            details={
                'validation_passed': result.validation_passed,
                'confidence': round(result.validation_confidence, 2)
            }
        ))

        # Test 5: Result contains all required fields
        required_fields = ['original_recommendations', 'adjusted_recommendations',
                          'feedback_intent', 'validation_passed', 'embeddings_updated']
        all_present = all(hasattr(result, field) for field in required_fields)
        self.results.append(TestResult(
            test_name='Loop: All Result Fields Present',
            test_category='Feedback Loop',
            passed=all_present,
            confidence=1.0 if all_present else 0.0,
            message='FeedbackLoopResult contains all required fields',
            details={'fields_present': sum(1 for f in required_fields if hasattr(result, f))}
        ))

    def _test_learning_gates(self):
        """Test safety gates for learning."""
        print("🚪 Testing Learning Gates...")

        # Test 1: High confidence learning accepted
        memory_good = FeedbackMemory(
            feedback_text="Perfect!",
            adjustment_type="energy_lower",
            original_preferences={'energy': 0.85},
            adjusted_preferences={'energy': 0.2},
            recommended_songs=["Song A", "Song B"],
            user_validated=True,
            validation_reason="Energy decreased"
        )

        updates = self.learner.learn_from_validated_feedback(memory_good)
        passed = len(updates) > 0  # Should update
        self.results.append(TestResult(
            test_name='Gate: High Confidence Learning Accepted',
            test_category='Learning Gates',
            passed=passed,
            confidence=0.95 if passed else 0.5,
            message=f'Updates applied: {len(updates) > 0}',
            details={'updates_count': len(updates)}
        ))

        # Test 2: Low confidence learning rejected
        memory_bad = FeedbackMemory(
            feedback_text="eh",
            adjustment_type="unknown",
            original_preferences={},
            adjusted_preferences={},
            recommended_songs=[],
            user_validated=False,
            validation_reason="Unknown"
        )

        updates_bad = self.learner.learn_from_validated_feedback(memory_bad)
        passed = len(updates_bad) == 0  # Should NOT update
        self.results.append(TestResult(
            test_name='Gate: Low Confidence Learning Rejected',
            test_category='Learning Gates',
            passed=passed,
            confidence=0.95 if passed else 0.5,
            message=f'Learning rejected (no updates): {len(updates_bad) == 0}',
            details={'updates_count': len(updates_bad), 'expected': 0}
        ))

        # Test 3: Validation gate checks actual change
        from src.learner import FeedbackValidator

        original = [{'energy': 0.8, 'valence': 0.7}]
        adjusted = [{'energy': 0.4, 'valence': 0.7}]

        passed_val, conf = FeedbackValidator.validate_energy_adjustment(
            original, adjusted, "lower"
        )

        passed = passed_val and conf > 0.7
        self.results.append(TestResult(
            test_name='Gate: Validation Checks Actual Change',
            test_category='Learning Gates',
            passed=passed,
            confidence=conf if passed else 0.5,
            message=f'Validation: {passed_val}, Confidence: {round(conf, 2)}',
            details={'passed': passed_val, 'confidence': round(conf, 2)}
        ))

    def _generate_report(self) -> Dict:
        """Generate structured evaluation report."""
        print("\n" + "=" * 80)
        print("📈 EVALUATION REPORT")
        print("=" * 80)
        print()

        # Group by category
        by_category = {}
        for result in self.results:
            if result.test_category not in by_category:
                by_category[result.test_category] = []
            by_category[result.test_category].append(result)

        # Print results by category
        total_passed = 0
        total_tests = 0
        category_scores = {}

        for category in sorted(by_category.keys()):
            tests = by_category[category]
            passed = sum(1 for t in tests if t.passed)
            total = len(tests)
            percentage = (passed / total * 100) if total > 0 else 0
            avg_confidence = sum(t.confidence for t in tests) / total if total > 0 else 0

            category_scores[category] = {
                'passed': passed,
                'total': total,
                'percentage': percentage,
                'confidence': avg_confidence
            }

            status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
            print(f"{status} {category}")
            print(f"   {passed}/{total} passed ({percentage:.0f}%)")
            print(f"   Confidence: {avg_confidence:.2f}/1.00")
            print()

            total_passed += passed
            total_tests += total

        # Overall summary
        overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        overall_confidence = sum(r.confidence for r in self.results) / len(self.results) if self.results else 0

        print("=" * 80)
        print(f"🎯 OVERALL SCORE: {total_passed}/{total_tests} ({overall_percentage:.0f}%)")
        print(f"📊 Average Confidence: {overall_confidence:.2f}/1.00")
        print("=" * 80)
        print()

        # Build report dict
        report = {
            'timestamp': '2026-08-02',
            'overall': {
                'tests_run': total_tests,
                'tests_passed': total_passed,
                'pass_rate': round(overall_percentage, 1),
                'confidence': round(overall_confidence, 2)
            },
            'by_category': category_scores,
            'individual_results': [r.to_dict() for r in self.results],
            'status': 'PASS' if overall_percentage == 100 else 'PARTIAL' if overall_percentage >= 80 else 'FAIL'
        }

        return report


def main():
    """Run evaluation harness."""
    harness = EvaluationHarness()
    report = harness.run_all_tests()

    # Print JSON report
    print("📄 Full Report (JSON):")
    print(json.dumps(report, indent=2))

    return 0 if report['overall']['pass_rate'] == 100 else 1


if __name__ == '__main__':
    sys.exit(main())
