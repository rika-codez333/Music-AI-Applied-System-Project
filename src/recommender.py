from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
import math
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Genre relationship graph: explicit semantic relationships for fuzzy matching
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

    SEMANTIC GENRE SIMILARITY: Fuzzy genre matching enables cross-genre discovery.
    - Exact match: 1.0
    - Related genres (e.g., pop → synth-pop): 0.75
    - Similar keywords (e.g., electronic → synthwave): 0.3-0.6
    - Different: 0.0-0.3

    This replaces the old all-or-nothing (0 or 2.3) genre matching with a continuous scale.
    """
    if not genre_a or not genre_b:
        return 0.0

    a = genre_a.lower().strip()
    b = genre_b.lower().strip()

    if a == b:
        return 1.0

    # Check explicit relationships (bidirectional)
    if a in GENRE_RELATIONSHIPS and b in GENRE_RELATIONSHIPS[a]:
        return 0.75
    if b in GENRE_RELATIONSHIPS and a in GENRE_RELATIONSHIPS[b]:
        return 0.75

    # String similarity with keyword matching boost
    string_sim = SequenceMatcher(None, a, b).ratio()
    a_words = set(a.split("-"))
    b_words = set(b.split("-"))
    shared_words = a_words & b_words

    if shared_words:
        keyword_boost = 0.3 * len(shared_words) / max(len(a_words), len(b_words))
        string_sim = min(1.0, string_sim + keyword_boost)

    return round(string_sim, 2)


# Mood Embedding Space: 2D coordinates (valence, energy)
# Enables semantic similarity instead of all-or-nothing matching
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

    MOOD EMBEDDINGS: Moods are mapped to 2D space (valence, energy).
    Similarity = 1.0 - (euclidean_distance / max_distance)

    - Exact match: 1.0
    - Very similar (calm ↔ chill): 0.85-0.99
    - Moderately similar (calm ↔ peaceful): 0.5-0.85
    - Different (calm ↔ intense): 0.0-0.5
    """
    if not mood_a or not mood_b:
        return 0.0

    a = mood_a.lower().strip()
    b = mood_b.lower().strip()

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

    # Convert distance to similarity
    similarity = 1.0 - (distance / max_distance)
    return round(max(0.0, similarity), 2)


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float
    release_decade: str
    mood_tags: str
    artist_familiarity: float
    production_quality: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    preferred_valence: float
    preferred_danceability: float
    preferred_tempo_bpm: float
    preferred_acousticness: float
    min_popularity: float = 30.0
    preferred_production_quality: float = 0.75
    prefer_artist_familiarity: bool = True

class ScoringStrategy(ABC):
    """Base class for different recommendation scoring strategies (Strategy Pattern)."""

    @abstractmethod
    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Score a song based on the strategy's weighting."""
        pass

class BalancedStrategy(ScoringStrategy):
    """Default balanced strategy: equal weight across all features."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Balanced scoring across all attributes."""
        weights = {
            'genre': 2.3, 'mood': 1.0, 'mood_mismatch': -0.5,
            'energy': 1.2, 'danceability': 1.2, 'valence': 1.0,
            'tempo_bpm': 0.6, 'acousticness': 0.6,
            'popularity': 0.8, 'production_quality': 0.6, 'artist_familiarity': 0.4,
        }
        return _compute_score(user_prefs, song, weights, k)

class GenreFirstStrategy(ScoringStrategy):
    """Genre-first: heavily weights genre matching."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Genre-first scoring: genre weight doubled."""
        weights = {
            'genre': 4.0, 'mood': 0.8, 'mood_mismatch': -0.3,
            'energy': 0.8, 'danceability': 0.8, 'valence': 0.6,
            'tempo_bpm': 0.4, 'acousticness': 0.4,
            'popularity': 0.4, 'production_quality': 0.3, 'artist_familiarity': 0.2,
        }
        return _compute_score(user_prefs, song, weights, k)

class MoodFirstStrategy(ScoringStrategy):
    """Mood-first: prioritizes mood matching and emotional alignment."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Mood-first scoring: mood weight tripled, valence boosted."""
        weights = {
            'genre': 1.0, 'mood': 2.5, 'mood_mismatch': -1.0,
            'energy': 1.5, 'danceability': 1.0, 'valence': 1.8,
            'tempo_bpm': 0.7, 'acousticness': 0.6,
            'popularity': 0.5, 'production_quality': 0.5, 'artist_familiarity': 0.3,
        }
        return _compute_score(user_prefs, song, weights, k)

class EnergyFocusedStrategy(ScoringStrategy):
    """Energy-focused: emphasizes energy and danceability for workout/party playlists."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Energy-focused scoring: energy and danceability doubled."""
        weights = {
            'genre': 1.0, 'mood': 0.6, 'mood_mismatch': -0.2,
            'energy': 2.5, 'danceability': 2.5, 'valence': 1.5,
            'tempo_bpm': 1.2, 'acousticness': 0.3,
            'popularity': 0.6, 'production_quality': 0.4, 'artist_familiarity': 0.3,
        }
        return _compute_score(user_prefs, song, weights, k)

class QualityFirstStrategy(ScoringStrategy):
    """Quality-first: prioritizes production quality and artistry."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Quality-first scoring: production quality and artist familiarity boosted."""
        weights = {
            'genre': 1.5, 'mood': 1.2, 'mood_mismatch': -0.4,
            'energy': 0.8, 'danceability': 0.8, 'valence': 0.8,
            'tempo_bpm': 0.6, 'acousticness': 0.8,
            'popularity': 1.0, 'production_quality': 1.8, 'artist_familiarity': 1.2,
        }
        return _compute_score(user_prefs, song, weights, k)

class PopularityDrivenStrategy(ScoringStrategy):
    """Popularity-driven: favors well-known songs and artists."""

    def score_song(self, user_prefs: Dict, song: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
        """Popularity-driven scoring: popularity and artist familiarity doubled."""
        weights = {
            'genre': 1.2, 'mood': 0.8, 'mood_mismatch': -0.3,
            'energy': 1.0, 'danceability': 1.0, 'valence': 0.8,
            'tempo_bpm': 0.5, 'acousticness': 0.4,
            'popularity': 2.0, 'production_quality': 0.8, 'artist_familiarity': 1.5,
        }
        return _compute_score(user_prefs, song, weights, k)

def _compute_score(user_prefs: Dict, song: Dict, weights: Dict, k: float = 1.0) -> Tuple[float, List[str]]:
    """Internal helper to compute score with given weights."""
    score = 0.0
    reasons = []
    contributions = {}

    numerical_features = ['energy', 'danceability', 'valence', 'tempo_bpm', 'acousticness', 'production_quality', 'artist_familiarity']
    for feature in numerical_features:
        pref_val = user_prefs.get(feature, 0.5)
        song_val = song.get(feature, 0.5)
        distance_squared = (pref_val - song_val) ** 2
        similarity = math.exp(-k * distance_squared)
        contribution = weights[feature] * similarity
        score += contribution
        contributions[feature] = (contribution, similarity, song_val, pref_val)

        if similarity > 0.9:
            reasons.append(f"🎯 {feature} excellent match ({song_val:.2f} ≈ {pref_val:.2f})")
        elif similarity > 0.7:
            reasons.append(f"✓ {feature} good match ({song_val:.2f})")

    # MOOD EMBEDDINGS: Fuzzy mood matching using semantic similarity
    mood_sim = mood_similarity(song['mood'], user_prefs.get('mood', ''))
    mood_contribution = weights['mood'] * mood_sim
    score += mood_contribution
    contributions['mood'] = (mood_contribution, mood_sim, song['mood'], user_prefs.get('mood'))

    if mood_sim >= 0.95:
        reasons.append(f"🎭 mood matches exactly ({song['mood']})")
    elif mood_sim >= 0.7:
        reasons.append(f"🎭 mood very similar ({song['mood']} ≈ {user_prefs.get('mood')})")
    elif mood_sim >= 0.4:
        reasons.append(f"~ mood somewhat similar ({song['mood']} ↔ {user_prefs.get('mood')})")
    else:
        # Proportional penalty: more penalty for very different moods
        mood_penalty = weights['mood_mismatch'] * (1.0 - mood_sim)
        score += mood_penalty
        reasons.append(f"⚠️ mood different ({song['mood']} ≠ {user_prefs.get('mood')})")

    # SEMANTIC GENRE SIMILARITY: Fuzzy genre matching (replaces all-or-nothing)
    genre_sim = genre_similarity(song['genre'], user_prefs.get('genre', ''))
    genre_contribution = weights['genre'] * genre_sim
    score += genre_contribution
    contributions['genre'] = (genre_contribution, genre_sim, song['genre'], user_prefs.get('genre'))

    if genre_sim >= 0.95:
        reasons.append(f"🎸 genre matches exactly ({song['genre']})")
    elif genre_sim >= 0.7:
        reasons.append(f"🎸 genre similar ({song['genre']} ≈ {user_prefs.get('genre')})")
    elif genre_sim >= 0.3:
        reasons.append(f"~ genre related ({song['genre']} ↔ {user_prefs.get('genre')})")

    min_popularity = user_prefs.get('min_popularity', 30.0)
    song_popularity = song.get('popularity', 50.0) / 100.0
    if song.get('popularity', 50.0) >= min_popularity:
        pop_similarity = min(1.0, song_popularity * 1.2)
        pop_contribution = weights['popularity'] * pop_similarity
        score += pop_contribution
        contributions['popularity'] = (pop_contribution, pop_similarity, song.get('popularity', 50.0), min_popularity)
        if pop_similarity > 0.8:
            reasons.append(f"⭐ popularity strong ({song.get('popularity', 50.0):.0f}/100)")
    else:
        score -= 0.3
        contributions['popularity'] = (-0.3, 0.0, song.get('popularity', 50.0), min_popularity)

    return round(score, 3), reasons

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    Supports Strategy pattern for different scoring modes.
    """
    def __init__(self, songs: List[Song], strategy: Optional[ScoringStrategy] = None):
        self.songs = songs
        self.strategy = strategy or BalancedStrategy()

    def recommend(self, user: UserProfile, k: int = 5, tuning_param: float = 1.0, verbose: bool = False, strategy: Optional[ScoringStrategy] = None) -> List[Song]:
        """
        Recommends top-k songs based on user profile using proximity-based content filtering.

        Args:
            user: UserProfile with preferences
            k: Number of recommendations (default 5)
            tuning_param: Gaussian k parameter (0.5=loose, 1.0=standard, 2.0=strict)
            verbose: If True, logs detailed scoring breakdown
            strategy: Optional ScoringStrategy to override instance strategy

        Returns:
            List of top-k Song objects, ranked by score
        """
        user_prefs = {
            'genre': user.favorite_genre,
            'mood': user.favorite_mood,
            'energy': user.target_energy,
            'valence': user.preferred_valence,
            'danceability': user.preferred_danceability,
            'tempo_bpm': user.preferred_tempo_bpm,
            'acousticness': user.preferred_acousticness,
            'min_popularity': user.min_popularity,
            'production_quality': user.preferred_production_quality,
            'artist_familiarity': user.prefer_artist_familiarity and 0.7 or 0.3,
        }

        strategy_to_use = strategy or self.strategy
        strategy_name = strategy_to_use.__class__.__name__

        if verbose:
            logger.info(f"Recommending top-{k} songs | User: genre={user.favorite_genre}, mood={user.favorite_mood}, energy={user.target_energy} | Strategy: {strategy_name}")

        scored_songs = []
        for song in self.songs:
            song_dict = {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'genre': song.genre,
                'mood': song.mood,
                'energy': song.energy,
                'tempo_bpm': song.tempo_bpm,
                'valence': song.valence,
                'danceability': song.danceability,
                'acousticness': song.acousticness,
                'popularity': song.popularity,
                'release_decade': song.release_decade,
                'mood_tags': song.mood_tags,
                'artist_familiarity': song.artist_familiarity,
                'production_quality': song.production_quality,
            }
            score, _ = strategy_to_use.score_song(user_prefs, song_dict, k=tuning_param)
            scored_songs.append((song, score))

        ranked = sorted(scored_songs, key=lambda x: -x[1])

        if verbose:
            logger.info(f"Top-{k} recommendations:")
            for idx, (song, score) in enumerate(ranked[:k], 1):
                logger.info(f"  {idx}. {song.title} ({song.artist}) - Score: {score:.3f}/7.9")

        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song, tuning_param: float = 1.0, verbose: bool = False, strategy: Optional[ScoringStrategy] = None) -> str:
        """
        Explains why a song was recommended to a user.

        Args:
            user: UserProfile with preferences
            song: Song to explain
            tuning_param: Gaussian k parameter
            verbose: If True, logs the explanation
            strategy: Optional ScoringStrategy to override instance strategy

        Returns:
            String explanation with score and contributing factors
        """
        user_prefs = {
            'genre': user.favorite_genre,
            'mood': user.favorite_mood,
            'energy': user.target_energy,
            'valence': user.preferred_valence,
            'danceability': user.preferred_danceability,
            'tempo_bpm': user.preferred_tempo_bpm,
            'acousticness': user.preferred_acousticness,
            'min_popularity': user.min_popularity,
            'production_quality': user.preferred_production_quality,
            'artist_familiarity': user.prefer_artist_familiarity and 0.7 or 0.3,
        }

        song_dict = {
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'genre': song.genre,
            'mood': song.mood,
            'energy': song.energy,
            'tempo_bpm': song.tempo_bpm,
            'valence': song.valence,
            'danceability': song.danceability,
            'acousticness': song.acousticness,
            'popularity': song.popularity,
            'release_decade': song.release_decade,
            'mood_tags': song.mood_tags,
            'artist_familiarity': song.artist_familiarity,
            'production_quality': song.production_quality,
        }

        strategy_to_use = strategy or self.strategy
        score, reasons = strategy_to_use.score_song(user_prefs, song_dict, k=tuning_param)
        explanation = f"Score: {score:.3f}/9.5\n" + "\n".join(reasons)

        if verbose:
            logger.info(f"Explaining '{song.title}': {explanation.replace(chr(10), ' | ')}")

        return explanation

def load_songs(csv_path: str) -> List[Dict]:
    """Parse songs from CSV into a list of dictionaries."""
    songs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
                'popularity': float(row['popularity']),
                'release_decade': row['release_decade'],
                'mood_tags': row['mood_tags'],
                'artist_familiarity': float(row['artist_familiarity']),
                'production_quality': float(row['production_quality']),
            }
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict, k: float = 1.0, verbose: bool = False) -> Tuple[float, List[str]]:
    """Score a song against user preferences using proximity-based Gaussian similarity.

    Enhanced weights with new attributes:
    - Genre match: +2.3 | Mood match: +1.0 | Mood mismatch: -0.5
    - Energy: +1.2 | Danceability: +1.2 | Valence: +1.0
    - Tempo: +0.6 | Acousticness: +0.6
    - Popularity: +0.8 | Production Quality: +0.6 | Artist Familiarity: +0.4
    - Max score: ~9.5

    Args:
        user_prefs: Reference song preferences (e.g., user's liked song or target profile)
        song: Song to score
        k: Gaussian tuning parameter (0.5=loose, 1.0=standard, 2.0=strict, default 1.0)
        verbose: If True, logs detailed scoring breakdown for this song

    Returns:
        (score, reasons): Score (0-9.5 max) and list of contributing factors
    """
    # Enhanced weights with new attributes
    weights = {
        'genre': 2.3,
        'mood': 1.0,
        'mood_mismatch': -0.5,
        'energy': 1.2,
        'danceability': 1.2,
        'valence': 1.0,
        'tempo_bpm': 0.6,
        'acousticness': 0.6,
        'popularity': 0.8,
        'production_quality': 0.6,
        'artist_familiarity': 0.4,
    }

    score = 0.0
    reasons = []
    contributions = {}

    if verbose:
        logger.info(f"Scoring '{song.get('title', 'Unknown')}' | k={k} (tuning: 0.5=loose, 1.0=standard, 2.0=strict)")

    # Numerical features: Gaussian similarity (proximity-based)
    numerical_features = ['energy', 'danceability', 'valence', 'tempo_bpm', 'acousticness', 'production_quality', 'artist_familiarity']
    for feature in numerical_features:
        pref_val = user_prefs.get(feature, 0.5)
        song_val = song.get(feature, 0.5)
        distance_squared = (pref_val - song_val) ** 2
        similarity = math.exp(-k * distance_squared)
        contribution = weights[feature] * similarity
        score += contribution
        contributions[feature] = (contribution, similarity, song_val, pref_val)

        if verbose:
            logger.debug(f"  {feature}: similarity={similarity:.3f}, contribution={contribution:.3f} ({song_val:.2f} vs {pref_val:.2f})")

        if similarity > 0.9:
            reasons.append(f"🎯 {feature} excellent match ({song_val:.2f} ≈ {pref_val:.2f})")
        elif similarity > 0.7:
            reasons.append(f"✓ {feature} good match ({song_val:.2f})")

    # Popularity scoring: higher popularity bonus (normalized 0-100 to 0-1)
    min_popularity = user_prefs.get('min_popularity', 30.0)
    song_popularity = song.get('popularity', 50.0) / 100.0
    if song.get('popularity', 50.0) >= min_popularity:
        pop_similarity = min(1.0, song_popularity * 1.2)
        pop_contribution = weights['popularity'] * pop_similarity
        score += pop_contribution
        contributions['popularity'] = (pop_contribution, pop_similarity, song.get('popularity', 50.0), min_popularity)
        if pop_similarity > 0.8:
            reasons.append(f"⭐ popularity strong ({song.get('popularity', 50.0):.0f}/100)")
    else:
        score -= 0.3  # Penalty for songs below minimum popularity threshold
        contributions['popularity'] = (-0.3, 0.0, song.get('popularity', 50.0), min_popularity)

    # Categorical features: exact match scoring
    mood_match = song['mood'] == user_prefs.get('mood')
    genre_match = song['genre'] == user_prefs.get('genre')

    if mood_match:
        score += weights['mood']
        contributions['mood'] = (weights['mood'], 1.0, song['mood'], user_prefs.get('mood'))
        reasons.append(f"🎭 mood matches ({song['mood']})")
        if verbose:
            logger.debug(f"  mood: MATCH +{weights['mood']:.1f}")
    else:
        mood_penalty = weights['mood_mismatch']
        score += mood_penalty
        contributions['mood'] = (mood_penalty, 0.0, song['mood'], user_prefs.get('mood'))
        reasons.append(f"⚠️ mood mismatch ({song['mood']} ≠ {user_prefs.get('mood')})")
        if verbose:
            logger.debug(f"  mood: MISMATCH {mood_penalty:.1f}")

    if genre_match:
        score += weights['genre']
        contributions['genre'] = (weights['genre'], 1.0, song['genre'], user_prefs.get('genre'))
        reasons.append(f"🎸 genre matches ({song['genre']})")
        if verbose:
            logger.debug(f"  genre: MATCH +{weights['genre']:.1f}")
    else:
        contributions['genre'] = (0.0, 0.0, song['genre'], user_prefs.get('genre'))
        if verbose:
            logger.debug(f"  genre: no match ({song['genre']} ≠ {user_prefs.get('genre')})")

    if verbose:
        logger.info(f"  ➜ Final score: {round(score, 3):.3f}/9.5 (max)")

    return round(score, 3), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, tuning_param: float = 1.0, verbose: bool = False, strategy: Optional[ScoringStrategy] = None) -> List[Tuple[Dict, float, List[str]]]:
    """Rank songs by score and return top-k recommendations.

    Args:
        user_prefs: User preference profile (e.g., favorite song or UserProfile as dict)
        songs: List of songs to score
        k: Number of recommendations to return (default 5)
        tuning_param: Gaussian k parameter (0.5=loose, 1.0=standard, 2.0=strict, default 1.0)
        verbose: If True, logs detailed scoring for each song
        strategy: Optional ScoringStrategy to use (defaults to BalancedStrategy)

    Returns:
        List of (song_dict, score, reasons) tuples, sorted by score descending
    """
    scored_songs = []
    strategy_to_use = strategy or BalancedStrategy()
    strategy_name = strategy_to_use.__class__.__name__

    if verbose:
        logger.info(f"Recommending top-{k} songs for user with prefs: {user_prefs} | Strategy: {strategy_name}")

    for song in songs:
        score, reasons = strategy_to_use.score_song(user_prefs, song, k=tuning_param)
        scored_songs.append((song, score, reasons))

    ranked = sorted(scored_songs, key=lambda x: -x[1])

    if verbose:
        logger.info(f"Top {k} recommendations:")
        for idx, (song, score, _) in enumerate(ranked[:k], 1):
            logger.info(f"  {idx}. {song.get('title', 'Unknown')} - {score:.3f}/9.5")

    return ranked[:k]
