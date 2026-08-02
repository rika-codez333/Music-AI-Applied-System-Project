"""
Persistence Layer — Save and load embeddings across sessions.

Enables the system to:
- Save learned embeddings to disk after each feedback iteration
- Load previous embeddings on startup
- Track learning history
- Compare before/after embeddings
"""

import json
import os
from typing import Dict, Tuple, List, Optional
from pathlib import Path
from datetime import datetime


class EmbeddingPersistence:
    """Manages saving and loading embeddings to/from disk."""

    def __init__(self, data_dir: str = ".embeddings"):
        """
        Initialize persistence layer.

        Args:
            data_dir: Directory to store embedding files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.embeddings_file = self.data_dir / "mood_embeddings.json"
        self.genres_file = self.data_dir / "genre_relationships.json"
        self.history_file = self.data_dir / "learning_history.json"

    def save_embeddings(
        self,
        mood_embeddings: Dict[str, Tuple[float, float]],
        genre_relationships: Dict[str, List[str]],
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Save embeddings to disk.

        Args:
            mood_embeddings: Dict of mood → (valence, energy) coordinates
            genre_relationships: Dict of genre → related_genres list
            metadata: Optional metadata (timestamp, learning_count, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert tuple coordinates to lists for JSON serialization
            mood_data = {mood: list(coords) for mood, coords in mood_embeddings.items()}

            embeddings_data = {
                "mood_embeddings": mood_data,
                "genre_relationships": genre_relationships,
                "metadata": metadata or {"timestamp": datetime.now().isoformat()},
            }

            with open(self.embeddings_file, "w") as f:
                json.dump(embeddings_data, f, indent=2)

            return True
        except Exception as e:
            print(f"❌ Error saving embeddings: {e}")
            return False

    def load_embeddings(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Load embeddings from disk.

        Returns:
            (mood_embeddings, genre_relationships) or (None, None) if not found
        """
        if not self.embeddings_file.exists():
            return None, None

        try:
            with open(self.embeddings_file, "r") as f:
                data = json.load(f)

            # Convert lists back to tuples
            mood_embeddings = {
                mood: tuple(coords) for mood, coords in data["mood_embeddings"].items()
            }
            genre_relationships = data["genre_relationships"]

            return mood_embeddings, genre_relationships
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return None, None

    def save_learning_history(self, history: List[Dict]) -> bool:
        """
        Save feedback learning history.

        Args:
            history: List of feedback records with results

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving learning history: {e}")
            return False

    def load_learning_history(self) -> Optional[List[Dict]]:
        """
        Load feedback learning history.

        Returns:
            List of feedback records or None if not found
        """
        if not self.history_file.exists():
            return None

        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading learning history: {e}")
            return None

    def get_embeddings_stats(self) -> Dict:
        """
        Get statistics about saved embeddings.

        Returns:
            Dict with info about embeddings (age, changes, etc.)
        """
        if not self.embeddings_file.exists():
            return {"status": "No embeddings saved yet"}

        try:
            with open(self.embeddings_file, "r") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            mood_count = len(data.get("mood_embeddings", {}))
            genre_count = len(data.get("genre_relationships", {}))

            return {
                "status": "Embeddings found",
                "timestamp": metadata.get("timestamp"),
                "moods_tracked": mood_count,
                "genres_tracked": genre_count,
                "file_size_bytes": self.embeddings_file.stat().st_size,
            }
        except Exception as e:
            return {"status": f"Error reading embeddings: {e}"}

    def cleanup(self, keep_history: bool = True) -> bool:
        """
        Clean up saved embeddings (reset system).

        Args:
            keep_history: If True, keep history file; if False, delete all

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.embeddings_file.exists():
                self.embeddings_file.unlink()

            if not keep_history and self.history_file.exists():
                self.history_file.unlink()

            return True
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False


def load_or_initialize_embeddings(
    persistence: EmbeddingPersistence,
    default_mood_embeddings: Dict[str, Tuple[float, float]],
    default_genres: Dict[str, List[str]],
) -> Tuple[Dict, Dict]:
    """
    Load saved embeddings or use defaults.

    Args:
        persistence: EmbeddingPersistence instance
        default_mood_embeddings: Default embeddings if none saved
        default_genres: Default genre relationships if none saved

    Returns:
        (mood_embeddings, genre_relationships)
    """
    mood_emb, genres = persistence.load_embeddings()

    if mood_emb is not None:
        print("✅ Loaded learned embeddings from disk")
        return mood_emb, genres

    print("ℹ️  Using default embeddings (no learned data found)")
    return default_mood_embeddings, default_genres
