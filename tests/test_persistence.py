"""Tests for persistence layer — save/load embeddings."""

import unittest
import tempfile
import shutil
from pathlib import Path
from src.persistence import EmbeddingPersistence, load_or_initialize_embeddings


class TestEmbeddingPersistence(unittest.TestCase):
    """Test saving and loading embeddings."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = EmbeddingPersistence(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_save_and_load_embeddings(self):
        """Test saving and loading embeddings."""
        original_moods = {
            "calm": (0.6, 0.2),
            "happy": (0.9, 0.7),
            "sad": (0.2, 0.3),
        }
        original_genres = {
            "pop": ["synth-pop", "indie-pop"],
            "electronic": ["synthwave", "edm"],
        }

        # Save
        success = self.persistence.save_embeddings(original_moods, original_genres)
        self.assertTrue(success)

        # Load
        loaded_moods, loaded_genres = self.persistence.load_embeddings()
        self.assertEqual(loaded_moods, original_moods)
        self.assertEqual(loaded_genres, original_genres)

    def test_load_nonexistent_embeddings(self):
        """Loading when no file exists returns None."""
        moods, genres = self.persistence.load_embeddings()
        self.assertIsNone(moods)
        self.assertIsNone(genres)

    def test_save_with_metadata(self):
        """Saving includes metadata."""
        moods = {"calm": (0.6, 0.2)}
        genres = {"pop": ["synth-pop"]}
        metadata = {"iterations": 5, "accuracy": 0.85}

        self.persistence.save_embeddings(moods, genres, metadata)
        loaded_moods, loaded_genres = self.persistence.load_embeddings()

        self.assertEqual(loaded_moods, moods)
        self.assertEqual(loaded_genres, genres)

    def test_save_learning_history(self):
        """Test saving feedback history."""
        history = [
            {"feedback": "I want something calmer", "validated": True},
            {"feedback": "More energetic", "validated": False},
        ]

        success = self.persistence.save_learning_history(history)
        self.assertTrue(success)

        loaded = self.persistence.load_learning_history()
        self.assertEqual(loaded, history)

    def test_load_nonexistent_history(self):
        """Loading nonexistent history returns None."""
        history = self.persistence.load_learning_history()
        self.assertIsNone(history)

    def test_embeddings_stats(self):
        """Test getting embedding statistics."""
        moods = {"calm": (0.6, 0.2), "happy": (0.9, 0.7)}
        genres = {"pop": ["synth-pop"], "rock": ["metal"]}

        self.persistence.save_embeddings(moods, genres)
        stats = self.persistence.get_embeddings_stats()

        self.assertEqual(stats["status"], "Embeddings found")
        self.assertEqual(stats["moods_tracked"], 2)
        self.assertEqual(stats["genres_tracked"], 2)
        self.assertIn("file_size_bytes", stats)

    def test_cleanup(self):
        """Test cleanup functionality."""
        moods = {"calm": (0.6, 0.2)}
        genres = {"pop": ["synth-pop"]}
        self.persistence.save_embeddings(moods, genres)

        # Verify files exist
        self.assertTrue(self.persistence.embeddings_file.exists())

        # Cleanup
        success = self.persistence.cleanup(keep_history=True)
        self.assertTrue(success)
        self.assertFalse(self.persistence.embeddings_file.exists())

    def test_load_or_initialize_with_saved(self):
        """load_or_initialize uses saved embeddings if available."""
        saved_moods = {"calm": (0.6, 0.2)}
        saved_genres = {"pop": ["synth-pop"]}

        self.persistence.save_embeddings(saved_moods, saved_genres)

        defaults_moods = {"calm": (0.5, 0.5)}  # Different defaults
        defaults_genres = {"pop": ["indie-pop"]}

        loaded_moods, loaded_genres = load_or_initialize_embeddings(
            self.persistence, defaults_moods, defaults_genres
        )

        # Should return saved, not defaults
        self.assertEqual(loaded_moods, saved_moods)
        self.assertEqual(loaded_genres, saved_genres)

    def test_load_or_initialize_with_defaults(self):
        """load_or_initialize uses defaults if no saved embeddings."""
        defaults_moods = {"calm": (0.5, 0.5)}
        defaults_genres = {"pop": ["indie-pop"]}

        loaded_moods, loaded_genres = load_or_initialize_embeddings(
            self.persistence, defaults_moods, defaults_genres
        )

        # Should return defaults
        self.assertEqual(loaded_moods, defaults_moods)
        self.assertEqual(loaded_genres, defaults_genres)


class TestEmbeddingPersistenceEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = EmbeddingPersistence(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_save_empty_embeddings(self):
        """Saving empty embeddings should work."""
        success = self.persistence.save_embeddings({}, {})
        self.assertTrue(success)

        moods, genres = self.persistence.load_embeddings()
        self.assertEqual(moods, {})
        self.assertEqual(genres, {})

    def test_save_large_embeddings(self):
        """Saving large embeddings should work."""
        moods = {f"mood_{i}": (i / 100, i / 100) for i in range(100)}
        genres = {f"genre_{i}": [f"subgenre_{i}_{j}" for j in range(5)] for i in range(50)}

        success = self.persistence.save_embeddings(moods, genres)
        self.assertTrue(success)

        loaded_moods, loaded_genres = self.persistence.load_embeddings()
        self.assertEqual(len(loaded_moods), 100)
        self.assertEqual(len(loaded_genres), 50)


if __name__ == "__main__":
    unittest.main()
