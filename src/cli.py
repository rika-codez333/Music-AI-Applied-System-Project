"""
Enhanced CLI with modes for recommendations, feedback loop, and A/B testing.

Modes:
1. Standard: Show recommendations for demo profiles (original behavior)
2. Feedback: Interactive feedback loop with embedding updates
3. A/B Testing: Compare original vs learned embeddings
4. Stats: Show learning statistics
"""

import sys
from typing import Optional, Dict, List
from .recommender import (
    Recommender, UserProfile, Song,
    BalancedStrategy, GenreFirstStrategy, MoodFirstStrategy,
    EnergyFocusedStrategy, QualityFirstStrategy, PopularityDrivenStrategy
)
from .feedback_loop import FeedbackLoop
from .learner import EmbeddingLearner
from .persistence import EmbeddingPersistence, load_or_initialize_embeddings
import csv


def load_songs(csv_path: str) -> List[Song]:
    """Load songs from CSV file."""
    songs = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                song = Song(
                    id=int(row.get("id", 0)),
                    title=row.get("title", ""),
                    artist=row.get("artist", ""),
                    genre=row.get("genre", ""),
                    mood=row.get("mood", ""),
                    energy=float(row.get("energy", 0.5)),
                    tempo_bpm=float(row.get("tempo_bpm", 100)),
                    valence=float(row.get("valence", 0.5)),
                    danceability=float(row.get("danceability", 0.5)),
                    acousticness=float(row.get("acousticness", 0.5)),
                    popularity=float(row.get("popularity", 50)),
                    release_decade=row.get("release_decade", "2020s"),
                    mood_tags=row.get("mood_tags", ""),
                    artist_familiarity=float(row.get("artist_familiarity", 0.5)),
                    production_quality=float(row.get("production_quality", 0.75)),
                )
                songs.append(song)
    except Exception as e:
        print(f"Error loading songs: {e}")
    return songs


def display_recommendations(songs: List[Song], user: UserProfile, k: int = 5):
    """Display recommendations in formatted output."""
    recommender = Recommender(songs)
    recommendations = recommender.recommend(user, k=k, verbose=True)

    print("\n" + "=" * 80)
    print(f"🎵 TOP {k} RECOMMENDATIONS")
    print("=" * 80 + "\n")

    for idx, song in enumerate(recommendations, 1):
        print(f"{idx}. {song.title} - {song.artist}")
        print(f"   Genre: {song.genre} | Mood: {song.mood}")
        print(f"   Energy: {song.energy:.2f} | Valence: {song.valence:.2f}")
        print()


def interactive_feedback_mode(songs: List[Song]):
    """Run interactive feedback loop with user."""
    print("\n" + "=" * 80)
    print("🎯 FEEDBACK LOOP MODE — Learn from Your Preferences")
    print("=" * 80)

    # Create user profile
    print("\nLet's create your music preference profile.")
    print("(Press Enter to use defaults shown in brackets)")

    genre = input("Favorite genre [lofi]: ").strip() or "lofi"
    mood = input("Favorite mood [calm]: ").strip() or "calm"
    energy = float(input("Target energy (0.0-1.0) [0.3]: ").strip() or "0.3")
    valence = float(input("Preferred valence (0.0-1.0) [0.6]: ").strip() or "0.6")

    user = UserProfile(
        favorite_genre=genre,
        favorite_mood=mood,
        target_energy=energy,
        preferred_valence=valence,
        preferred_danceability=0.4,
        preferred_tempo_bpm=100,
        preferred_acousticness=0.7,
    )

    # Initialize feedback loop with persistence
    persistence = EmbeddingPersistence()
    learner = EmbeddingLearner()
    recommender = Recommender(songs)
    loop = FeedbackLoop(recommender, learner)

    print("\n" + "=" * 80)
    print("Starting feedback loop. Type 'quit' to exit.")
    print("=" * 80 + "\n")

    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 ITERATION {iteration}")
        print("-" * 80)

        # Get recommendations
        original = recommender.recommend(user, k=5)
        print(f"Original recommendations:")
        for song in original[:3]:
            print(f"  • {song.title} ({song.genre}, energy={song.energy:.2f})")

        # Get feedback
        feedback = input("\nYour feedback (or 'quit'): ").strip()
        if feedback.lower() == "quit":
            break

        if not feedback:
            continue

        # Process feedback through loop
        result = loop.process_feedback(user, feedback, k=5)

        print(f"\n✓ Feedback processed:")
        print(f"  Adjustment: {result.feedback_intent.adjustment_type.value}")
        print(f"  Confidence: {result.feedback_intent.confidence:.2f}")
        print(f"  Validation: {'✅ PASSED' if result.validation_passed else '❌ FAILED'}")

        if result.embeddings_updated:
            print(f"  Embeddings updated: {len(result.embeddings_updated)} changes")
            for key, value in list(result.embeddings_updated.items())[:3]:
                print(f"    • {key}: {value:+.4f}")

        # Show adjusted recommendations
        print(f"\nAdjusted recommendations:")
        for title in result.adjusted_recommendations[:3]:
            print(f"  • {title}")

    # Save embeddings after loop
    stats = learner.get_learning_summary()
    print(f"\n" + "=" * 80)
    print(f"📊 LEARNING SUMMARY")
    print(f"=" * 80)
    print(f"Total feedback iterations: {stats['feedback_count']}")
    print(f"Validated iterations: {stats['validated_count']}")
    print(f"Accuracy: {stats['accuracy']*100:.1f}%")
    print(f"Embeddings updated: {stats['embeddings_updated']}")

    # Ask to save
    save = input("\nSave learned embeddings? (y/n): ").strip().lower() == "y"
    if save:
        mood_emb, genres = learner.get_current_embeddings()
        persistence.save_embeddings(
            mood_emb,
            genres,
            {"iterations": iteration, "accuracy": stats["accuracy"]},
        )
        print("✅ Embeddings saved!")


def ab_testing_mode(songs: List[Song]):
    """Compare original vs learned embeddings."""
    print("\n" + "=" * 80)
    print("🧪 A/B TESTING MODE — Compare Original vs Learned")
    print("=" * 80)

    persistence = EmbeddingPersistence()
    history = persistence.load_learning_history()

    if not history:
        print("❌ No learning history found. Run feedback mode first!")
        return

    print(f"\n📊 Learning Statistics:")
    print(f"  Total feedback iterations: {len(history)}")

    validated = sum(1 for h in history if h.get("validation_passed"))
    accuracy = validated / len(history) if history else 0
    print(f"  Validated iterations: {validated}")
    print(f"  Accuracy: {accuracy*100:.1f}%")

    # Create sample user
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="calm",
        target_energy=0.3,
        preferred_valence=0.6,
        preferred_danceability=0.4,
        preferred_tempo_bpm=100,
        preferred_acousticness=0.7,
    )

    # Get recommendations with learned embeddings
    persistence_loaded = EmbeddingPersistence()
    from .recommender import MOOD_EMBEDDINGS, GENRE_RELATIONSHIPS

    learned_moods, learned_genres = persistence_loaded.load_embeddings()
    if learned_moods:
        print("\n✅ Comparing recommendations (learned embeddings available)")
    else:
        print("\nℹ️  No learned embeddings found, using defaults")


def stats_mode():
    """Show learning statistics."""
    print("\n" + "=" * 80)
    print("📊 LEARNING STATISTICS")
    print("=" * 80)

    persistence = EmbeddingPersistence()
    stats = persistence.get_embeddings_stats()

    for key, value in stats.items():
        print(f"{key}: {value}")

    history = persistence.load_learning_history()
    if history:
        print(f"\nLast 5 feedback iterations:")
        for entry in history[-5:]:
            timestamp = entry.get("timestamp", "unknown")
            passed = entry.get("validation_passed", False)
            status = "✅" if passed else "❌"
            print(f"  {status} {entry.get('feedback_text', '')[:50]}")


def standard_mode():
    """Run original demonstration mode."""
    print("\n" + "=" * 80)
    print("🎵 STANDARD MODE — Demo Recommendations")
    print("=" * 80)

    songs = load_songs("data/songs.csv")

    profiles = {
        "High-Energy Pop": UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.9,
            preferred_valence=0.8,
            preferred_danceability=0.8,
            preferred_tempo_bpm=130,
            preferred_acousticness=0.2,
            min_popularity=70,
        ),
        "Chill Lofi": UserProfile(
            favorite_genre="lofi",
            favorite_mood="calm",
            target_energy=0.2,
            preferred_valence=0.6,
            preferred_danceability=0.4,
            preferred_tempo_bpm=100,
            preferred_acousticness=0.8,
            min_popularity=50,
        ),
        "Deep Intense Rock": UserProfile(
            favorite_genre="rock",
            favorite_mood="intense",
            target_energy=0.85,
            preferred_valence=0.5,
            preferred_danceability=0.6,
            preferred_tempo_bpm=140,
            preferred_acousticness=0.2,
            min_popularity=40,
        ),
    }

    for profile_name, user in profiles.items():
        print(f"\n\n📊 USER PROFILE: {profile_name}")
        display_recommendations(songs, user, k=5)


def show_help():
    """Display help message."""
    print("""
🎵 MUSIC AI RECOMMENDER — CLI HELP

Usage: python3 -m src.cli [MODE]

Modes:
  standard    - Show demo recommendations (default)
  feedback    - Interactive feedback loop with learning
  ab-test     - Compare original vs learned embeddings
  stats       - Show learning statistics
  help        - Show this message

Examples:
  python3 -m src.cli
  python3 -m src.cli feedback
  python3 -m src.cli stats
""")


def main():
    """Main CLI entry point."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "standard"

    if mode == "feedback":
        songs = load_songs("data/songs.csv")
        interactive_feedback_mode(songs)

    elif mode == "ab-test":
        ab_testing_mode(load_songs("data/songs.csv"))

    elif mode == "stats":
        stats_mode()

    elif mode in ("help", "-h", "--help"):
        show_help()

    else:
        standard_mode()


if __name__ == "__main__":
    main()
