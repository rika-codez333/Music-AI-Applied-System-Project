"""
Tests for the Agentic Feedback Loop — Plan → Act → Validate → Learn

Tests validate that:
1. Feedback is parsed into structured intent
2. User preferences are adjusted based on feedback
3. Recommendations change appropriately
4. Validation correctly identifies successful adjustments
5. Embeddings are updated when validation passes
"""

import unittest
from src.feedback import FeedbackAnalyzer, AdjustmentType, FeedbackIntent
from src.learner import FeedbackValidator, FeedbackMemory, EmbeddingLearner
from src.feedback_loop import FeedbackLoop


class TestFeedbackAnalyzer(unittest.TestCase):
    """Test the feedback parsing (PLAN phase)."""

    def setUp(self):
        self.analyzer = FeedbackAnalyzer()

    def test_parse_energy_lower_feedback(self):
        """User wants lower energy."""
        intent = self.analyzer.parse("I liked that song but it was too energetic")
        self.assertEqual(intent.adjustment_type, AdjustmentType.ENERGY_LOWER)
        self.assertGreater(intent.confidence, 0.8)

    def test_parse_energy_higher_feedback(self):
        """User wants higher energy."""
        intent = self.analyzer.parse("Give me something more upbeat and energetic")
        self.assertEqual(intent.adjustment_type, AdjustmentType.ENERGY_HIGHER)
        self.assertGreater(intent.confidence, 0.8)

    def test_parse_softer_feedback(self):
        """User wants softer music."""
        intent = self.analyzer.parse("I want something softer and more relaxing")
        self.assertEqual(intent.adjustment_type, AdjustmentType.OVERALL_SOFTER)

    def test_parse_mood_feedback(self):
        """User wants different mood."""
        intent = self.analyzer.parse("Give me something more happy and uplifting")
        self.assertEqual(intent.adjustment_type, AdjustmentType.MOOD_SHIFT)

    def test_extract_song_title_quoted(self):
        """Extract quoted song title."""
        intent = self.analyzer.parse('I liked "Midnight Coding" but wanted something calmer')
        self.assertEqual(intent.liked_song, "Midnight Coding")

    def test_extract_song_title_pattern(self):
        """Extract song title from 'liked X but' pattern."""
        intent = self.analyzer.parse("I liked Neon Nights but wanted it calmer")
        self.assertEqual(intent.liked_song, "Neon Nights")

    def test_case_insensitive_parsing(self):
        """Parsing is case-insensitive."""
        intent1 = self.analyzer.parse("LESS ENERGETIC")
        intent2 = self.analyzer.parse("less energetic")
        self.assertEqual(intent1.adjustment_type, intent2.adjustment_type)

    def test_very_keyword_increases_target(self):
        """'Very' keyword sets stronger target value."""
        intent_normal = self.analyzer.parse("I want something calmer")
        intent_very = self.analyzer.parse("I want something VERY much calmer")

        self.assertLess(intent_very.target_value, intent_normal.target_value,
                       "Very keyword should increase magnitude")

    def test_apply_energy_lower_to_profile(self):
        """Applying energy_lower feedback adjusts user profile."""
        user_prefs = {
            'energy': 0.8,
            'tempo_bpm': 150,
            'valence': 0.7,
        }

        intent = self.analyzer.parse("I want something calmer")
        adjusted = self.analyzer.apply_to_profile(intent, user_prefs)

        self.assertLess(adjusted['energy'], user_prefs['energy'],
                       "Energy should decrease")
        self.assertLess(adjusted['tempo_bpm'], user_prefs['tempo_bpm'],
                       "Tempo should decrease")

    def test_apply_mood_shift_to_profile(self):
        """Applying mood shift feedback adjusts valence/energy."""
        user_prefs = {
            'valence': 0.5,
            'energy': 0.5,
        }

        intent = self.analyzer.parse("I want something more happy")
        adjusted = self.analyzer.apply_to_profile(intent, user_prefs)

        self.assertGreater(adjusted['valence'], user_prefs['valence'],
                          "Valence should increase for happy")


class TestFeedbackValidator(unittest.TestCase):
    """Test the validation (VALIDATE phase)."""

    def test_validate_energy_lower_success(self):
        """Validation passes when energy decreases."""
        original = [
            {'energy': 0.8, 'title': 'Song A'},
            {'energy': 0.7, 'title': 'Song B'},
        ]
        adjusted = [
            {'energy': 0.3, 'title': 'Song C'},
            {'energy': 0.4, 'title': 'Song D'},
        ]

        passed, confidence = FeedbackValidator.validate_energy_adjustment(
            original, adjusted, "lower"
        )

        self.assertTrue(passed, "Should validate energy decrease")
        self.assertGreater(confidence, 0.7, "Should have high confidence")

    def test_validate_energy_higher_success(self):
        """Validation passes when energy increases."""
        original = [
            {'energy': 0.3, 'title': 'Song A'},
            {'energy': 0.4, 'title': 'Song B'},
        ]
        adjusted = [
            {'energy': 0.8, 'title': 'Song C'},
            {'energy': 0.9, 'title': 'Song D'},
        ]

        passed, confidence = FeedbackValidator.validate_energy_adjustment(
            original, adjusted, "higher"
        )

        self.assertTrue(passed, "Should validate energy increase")
        self.assertGreater(confidence, 0.7, "Should have high confidence")

    def test_validate_energy_lower_failure(self):
        """Validation fails when energy doesn't decrease."""
        original = [
            {'energy': 0.5, 'title': 'Song A'},
            {'energy': 0.5, 'title': 'Song B'},
        ]
        adjusted = [
            {'energy': 0.6, 'title': 'Song C'},  # Actually increased!
            {'energy': 0.7, 'title': 'Song D'},
        ]

        passed, confidence = FeedbackValidator.validate_energy_adjustment(
            original, adjusted, "lower"
        )

        self.assertFalse(passed, "Should fail when energy increases")
        self.assertLess(confidence, 0.7, "Should have low confidence")

    def test_validate_mood_adjustment(self):
        """Validation checks if mood/valence profile changed."""
        original = [
            {'valence': 0.7, 'title': 'Song A'},
            {'valence': 0.8, 'title': 'Song B'},
        ]
        adjusted = [
            {'valence': 0.2, 'title': 'Song C'},
            {'valence': 0.3, 'title': 'Song D'},
        ]

        passed, confidence = FeedbackValidator.validate_mood_adjustment(
            original, adjusted
        )

        self.assertTrue(passed, "Should detect mood change")
        self.assertGreater(confidence, 0.7, "Should have high confidence")

    def test_validate_empty_songs_returns_false(self):
        """Validation fails gracefully with empty lists."""
        passed, confidence = FeedbackValidator.validate_energy_adjustment([], [], "lower")
        self.assertFalse(passed, "Should handle empty lists")


class TestEmbeddingLearner(unittest.TestCase):
    """Test the learning (LEARN phase)."""

    def test_learner_initialization(self):
        """Learner initializes with current embeddings."""
        learner = EmbeddingLearner()
        moods, genres = learner.get_current_embeddings()

        self.assertIn("calm", moods, "Should have calm mood")
        self.assertIn("happy", moods, "Should have happy mood")
        self.assertIn("pop", genres, "Should have pop genre")

    def test_record_feedback(self):
        """Learner records feedback in memory."""
        learner = EmbeddingLearner()
        memory = FeedbackMemory(
            feedback_text="I want something calmer",
            adjustment_type="energy_lower",
            original_preferences={'energy': 0.8},
            adjusted_preferences={'energy': 0.3},
            recommended_songs=['Song A', 'Song B', 'Song C'],
            user_validated=True,
        )

        learner.record_feedback(memory)
        self.assertEqual(len(learner.memory), 1)

    def test_learn_energy_lower_updates_embedding(self):
        """Learning from validated energy_lower feedback updates embeddings."""
        learner = EmbeddingLearner()

        original_embed = learner.mood_embeddings['calm']

        memory = FeedbackMemory(
            feedback_text="I want something calmer",
            adjustment_type="energy_lower",
            original_preferences={'mood': 'calm', 'energy': 0.8},
            adjusted_preferences={'mood': 'calm', 'energy': 0.3},
            recommended_songs=['Song A', 'Song B', 'Song C'],
            user_validated=True,
        )

        learner.record_feedback(memory)
        updates = learner.learn_from_validated_feedback(memory)

        new_embed = learner.mood_embeddings['calm']

        self.assertGreater(len(updates), 0, "Should make updates")
        self.assertNotEqual(original_embed, new_embed,
                           "Embedding should change after learning")

    def test_learn_unvalidated_feedback_no_update(self):
        """Learning skips unvalidated feedback."""
        learner = EmbeddingLearner()
        original_embed = learner.mood_embeddings['calm']

        memory = FeedbackMemory(
            feedback_text="I want something calmer",
            adjustment_type="energy_lower",
            original_preferences={'mood': 'calm'},
            adjusted_preferences={'mood': 'calm'},
            recommended_songs=['Song A'],
            user_validated=False,  # User rejected
        )

        learner.record_feedback(memory)
        updates = learner.learn_from_validated_feedback(memory)

        self.assertEqual(len(updates), 0, "Should not update on unvalidated feedback")
        self.assertEqual(original_embed, learner.mood_embeddings['calm'],
                        "Embedding should not change")

    def test_get_learning_summary(self):
        """Learning summary reflects feedback history."""
        learner = EmbeddingLearner()

        # Add validated feedback
        for i in range(3):
            memory = FeedbackMemory(
                feedback_text=f"Feedback {i}",
                adjustment_type="energy_lower",
                original_preferences={'mood': 'calm'},
                adjusted_preferences={'mood': 'calm'},
                recommended_songs=['Song A'],
                user_validated=True,
            )
            learner.record_feedback(memory)
            learner.learn_from_validated_feedback(memory)

        summary = learner.get_learning_summary()

        self.assertEqual(summary['feedback_count'], 3)
        self.assertEqual(summary['validated_count'], 3)
        self.assertGreater(summary['accuracy'], 0.0)


class TestFeedbackLoopIntegration(unittest.TestCase):
    """Integration tests for the full feedback loop."""

    def test_feedback_loop_parsing(self):
        """Test PLAN phase: parsing."""
        analyzer = FeedbackAnalyzer()
        intent = analyzer.parse("I liked that song but wanted something calmer")

        self.assertEqual(intent.adjustment_type, AdjustmentType.ENERGY_LOWER)
        self.assertGreater(intent.confidence, 0.7)

    def test_feedback_loop_adjustment(self):
        """Test ACT phase: adjustment."""
        analyzer = FeedbackAnalyzer()
        user_prefs = {'energy': 0.8, 'tempo_bpm': 150}

        intent = analyzer.parse("I want something calmer")
        adjusted = analyzer.apply_to_profile(intent, user_prefs)

        self.assertLess(adjusted['energy'], user_prefs['energy'])

    def test_feedback_loop_validation(self):
        """Test VALIDATE phase: validation."""
        original = [
            {'energy': 0.8, 'title': 'Song A'},
            {'energy': 0.7, 'title': 'Song B'},
        ]
        adjusted = [
            {'energy': 0.3, 'title': 'Song C'},
            {'energy': 0.2, 'title': 'Song D'},
        ]

        passed, conf, reason = FeedbackValidator.validate_recommendation(
            original, adjusted, "energy_lower"
        )

        self.assertTrue(passed, "Should validate energy decrease")
        self.assertIn("Energy", reason)

    def test_feedback_loop_learning(self):
        """Test LEARN phase: learning."""
        learner = EmbeddingLearner()

        memory = FeedbackMemory(
            feedback_text="I want something calmer",
            adjustment_type="energy_lower",
            original_preferences={'mood': 'calm', 'energy': 0.8},
            adjusted_preferences={'mood': 'calm', 'energy': 0.3},
            recommended_songs=['Song A', 'Song B'],
            user_validated=True,
        )

        learner.record_feedback(memory)
        updates = learner.learn_from_validated_feedback(memory)

        self.assertGreater(len(updates), 0, "Should learn from validated feedback")


if __name__ == '__main__':
    unittest.main()
