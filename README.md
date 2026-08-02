# 🎵 Music AI Recommender System — AI110 Applied AI Systems Project

A **content-based music recommender system** with **semantic understanding** and **agentic learning capabilities**. Built to demonstrate advanced AI features: Agentic Workflow, RAG, Reliability Systems, and Adaptive Learning.

## ✅ Project Status: COMPLETE

All 3 core phases implemented and tested with 84 passing tests:

| Phase | Feature | Tests | Status |
|-------|---------|-------|--------|
| 1 | Semantic Genre Similarity | 13 | ✅ Complete |
| 2 | Mood Embeddings | 18 | ✅ Complete |
| 3 | Agentic Feedback Loop | 24 | ✅ Complete |
| — | Core Recommender | 25 | ✅ Complete |
| — | Playlist Management | 4 | ✅ Complete |
| **TOTAL** | **All Tests** | **84** | **✅ All Passing** |

## 🚀 Quick Start

```bash
# Install & test
python3 -m pytest -v

# Run recommendations
python3 -m src.main

# Test adversarial profiles
python3 src/adversarial_test.py
```

## 🎯 Three Advanced AI Features

### 1. Semantic Genre Similarity ✅ COMPLETE

**Problem**: "synthwave" and "electronic" treated as different.  
**Solution**: Fuzzy genre matching (0.75 similarity score).

```
User prefers: electronic
Song is:      synthwave
Before:       0.0 (blocked)
After:        1.72 (75% credit, discovery enabled)
```

**Key Achievement**: Genre scores now continuous 0.0-2.3 instead of binary.  
**See**: [SEMANTIC_GENRE_SIMILARITY.md](SEMANTIC_GENRE_SIMILARITY.md)

---

### 2. Mood Embeddings ✅ COMPLETE

**Problem**: "calm", "chill", "relaxed" treated as different.  
**Solution**: 2D embedding space (valence × energy).

```
Mood space:
    energetic (1.0)
         ↑
    intense (0.4, 0.95)    excited (0.8, 0.9)
         │
calm ←───•───→ happy (0.9, 0.7)
(0.6, 0.2)
         │
      sad (0.2, 0.3)
         ↓
      calm (0.0)
```

**Example Similarities**:
- calm ↔ calm: 1.00 (exact)
- calm ↔ chill: 0.95 (very similar)
- calm ↔ intense: 0.45 (opposite)

**Key Achievement**: Mood scores now proportional 0.0-1.0 instead of binary.  
**See**: [MOOD_EMBEDDINGS.md](MOOD_EMBEDDINGS.md)

---

### 3. Agentic Feedback Loop ✅ COMPLETE

**Problem**: System never learned from feedback.  
**Solution**: Full Plan→Act→Validate→Learn workflow.

```
User: "I liked Song X but wanted something calmer"
  ↓ [PLAN: Parse feedback]
→ Adjustment: energy_lower, target=0.3
  ↓ [ACT: Adjust preferences]
→ Top-5 songs with energy=0.3 instead of 0.8
  ↓ [VALIDATE: Check if worked]
→ Energy decreased ✓ Confidence: 0.85
  ↓ [LEARN: Update embeddings]
→ MOOD_EMBEDDINGS["calm"] energy: 0.20→0.18
```

**Key Achievement**: System learns from feedback and improves over time.  
**See**: [AGENTIC_FEEDBACK_LOOP.md](AGENTIC_FEEDBACK_LOOP.md)

**Formula**:
```
TOTAL_SCORE = genre_contrib + mood_contrib + energy_contrib + 
              danceability_contrib + valence_contrib + tempo_contrib + acousticness_contrib

Where:
- genre_contrib = 2.3 if (song.genre == user.favorite_genre) else 0.0
- mood_contrib = 1.0 if (song.mood == user.favorite_mood) else -0.5
- numeric_contrib = weight × exp(-k × (user_preference - song_value)²)
- k = tuning_param (0.5=loose/forgiving, 1.0=standard, 2.0=strict)
```

**Intuition**: The system rewards songs that match audio features *close to* what the user likes (via Gaussian), without penalizing songs that differ. Genre and mood are exact-match categorical filters—a critical design choice that emphasizes user intent over serendipity.

**Ranking & Recommendation**:
1. Score all available songs independently using the formula above
2. Sort by total score (descending)
3. Return top-k recommendations with explainable reasons for each pick
4. Explanations highlight which features contributed most to the score (marked with 🎯 for excellent matches >0.9 similarity, ✓ for good matches >0.7)

### Potential Biases in This System

1. **Heavy Genre Preference**: Genre is weighted at 2.0 (25.6% of max score), making exact-match genre the strongest factor. This system might **over-prioritize familiar genres and miss great cross-genre discoveries**. A user who loves "pop" might miss an amazing "lofi" acoustic track with identical energy/mood characteristics.

2. **Categorical Mood Rigidity**: Mood uses exact matching (chill = chill, intense = intense), with no similarity metric. **A song with mood="chill" won't match a user preferring mood="relaxed," even though they're semantically identical.** This creates artificial "cliffs" in recommendations.

3. **Gaussian Centering on User Preferences**: The Gaussian similarity rewards songs matching the user's *exact* preferences (e.g., target_energy = 0.5). This can **suppress unexpected discoveries**—a high-energy song that matches mood and genre perfectly might score lower than a mediocre low-energy song if the user's target_energy doesn't match.

4. **Tiny Catalog Bias**: Recommendations are only as diverse as the training data. A 30-song catalog won't find the perfect song in a library of millions.

5. **No Temporal or Popularity Signals**: The system doesn't account for song release date, artist popularity, or trending status. Very old or niche songs might not be recommended despite matching features.

6. **No Feedback Loop**: The system is static—it doesn't learn from user behavior (skips, replays, saves). Real systems like Spotify adjust weights after each interaction.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

### Running the Evaluation Scripts

**Standard Profile Evaluation** (3 diverse user profiles):
```bash
python -m src.main
```

This runs recommendations for:
1. **High-Energy Pop** — upbeat, feel-good music
2. **Chill Lofi** — relaxing, low-energy focus music
3. **Deep Intense Rock** — heavy, powerful rock

**Adversarial Testing** (4 edge-case profiles to stress-test the system):
```bash
python src/adversarial_test.py
```

This tests how the system handles:
1. **Contradictory Preferences** — conflicting signals (rock + happy + low energy)
2. **Extremely Picky** — extreme feature values (energy=0.95 with rare genre)
3. **Impossible Combo** — semantically contradictory preferences (intense lofi)
4. **Niche Mood** — non-existent mood category in the catalog

---

## System Evaluation: Multi-Profile Testing

This section documents how the recommender performs across **three distinct user profiles** representing different musical tastes and contexts. Each profile was evaluated on the same song catalog to assess recommendation quality, diversity, and scoring consistency.

### Profile 1: High-Energy Pop Listener
**Preferences**: `genre=pop, mood=happy, energy=0.9`  
**Context**: Upbeat, feel-good pop music with maximum energy

```
======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Sunrise City - Neon Echo
   Score: 7.03/7.9 │██████████████████████████░░░░│ 89%
   Why you'll love it:
     • 🎯 energy excellent match (0.82 ≈ 0.90)
     • 🎯 danceability excellent match (0.79 ≈ 0.50)
     • ✓ valence good match (0.84)
     • 🎯 acousticness excellent match (0.18 ≈ 0.50)
     • 🎭 mood matches (happy)
     • 🎸 genre matches (pop)

----------------------------------------------------------------------

2. Gym Hero - Max Pulse
   Score: 5.46/7.9 │████████████████████░░░░░░░░░░│ 69%
   Why you'll love it:
     • 🎯 energy excellent match (0.93 ≈ 0.90)
     • ✓ danceability good match (0.88)
     • 🎯 valence excellent match (0.77 ≈ 0.50)
     • ✓ acousticness good match (0.05)
     • ⚠️ mood mismatch (intense ≠ happy)
     • 🎸 genre matches (pop)

----------------------------------------------------------------------

3. Rooftop Lights - Indigo Parade
   Score: 4.75/7.9 │██████████████████░░░░░░░░░░░░│ 60%
   Why you'll love it:
     • 🎯 energy excellent match (0.76 ≈ 0.90)
     • 🎯 danceability excellent match (0.82 ≈ 0.50)
     • 🎯 valence excellent match (0.81 ≈ 0.50)
     • 🎯 acousticness excellent match (0.35 ≈ 0.50)
     • 🎭 mood matches (happy)

----------------------------------------------------------------------

4. Storm Runner - Voltline
   Score: 3.38/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.91 ≈ 0.90)
     • 🎯 danceability excellent match (0.66 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • ✓ acousticness good match (0.10)
     • ⚠️ mood mismatch (intense ≠ happy)

----------------------------------------------------------------------

5. Night Drive Loop - Neon Echo
   Score: 3.37/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.75 ≈ 0.90)
     • 🎯 danceability excellent match (0.73 ≈ 0.50)
     • 🎯 valence excellent match (0.49 ≈ 0.50)
     • 🎯 acousticness excellent match (0.22 ≈ 0.50)
     • ⚠️ mood mismatch (moody ≠ happy)

======================================================================
```

**Analysis**: The High-Energy Pop profile now demonstrates improved genre coherence. "Sunrise City" remains #1 with genre and mood matches (89%), while "Gym Hero" (#2) is also a strong pop match. Critically, "Storm Runner" (a rock song) has dropped from #4 to a 3.38 score (43%) due to the new mood penalty (-0.5) and reduced energy weight. This shows the system now better prioritizes genre-coherent recommendations while still allowing feature-based discovery within that genre.

---

### Profile 2: Chill Lofi Listener
**Preferences**: `genre=lofi, mood=calm, energy=0.2`  
**Context**: Relaxing, low-energy lofi beats for focus and relaxation

```
======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Midnight Coding - LoRoom
   Score: 5.70/7.9 │█████████████████████░░░░░░░░░│ 72%
   Why you'll love it:
     • 🎯 energy excellent match (0.42 ≈ 0.20)
     • 🎯 danceability excellent match (0.62 ≈ 0.50)
     • 🎯 valence excellent match (0.56 ≈ 0.50)
     • 🎯 acousticness excellent match (0.71 ≈ 0.50)
     • ⚠️ mood mismatch (chill ≠ calm)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

2. Focus Flow - LoRoom
   Score: 5.69/7.9 │█████████████████████░░░░░░░░░│ 72%
   Why you'll love it:
     • 🎯 energy excellent match (0.40 ≈ 0.20)
     • 🎯 danceability excellent match (0.60 ≈ 0.50)
     • 🎯 valence excellent match (0.59 ≈ 0.50)
     • 🎯 acousticness excellent match (0.78 ≈ 0.50)
     • ⚠️ mood mismatch (focused ≠ calm)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

3. Library Rain - Paper Lanterns
   Score: 5.68/7.9 │█████████████████████░░░░░░░░░│ 72%
   Why you'll love it:
     • 🎯 energy excellent match (0.35 ≈ 0.20)
     • 🎯 danceability excellent match (0.58 ≈ 0.50)
     • 🎯 valence excellent match (0.60 ≈ 0.50)
     • ✓ acousticness good match (0.86)
     • ⚠️ mood mismatch (chill ≠ calm)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

4. Whispers in the Rain - Indie Soul
   Score: 3.43/7.9 │█████████████░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.35 ≈ 0.20)
     • 🎯 danceability excellent match (0.54 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • 🎯 acousticness excellent match (0.78 ≈ 0.50)
     • ⚠️ mood mismatch (melancholic ≠ calm)

----------------------------------------------------------------------

5. Midnight Melancholy - Blue Notes Trio
   Score: 3.37/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.45 ≈ 0.20)
     • 🎯 danceability excellent match (0.64 ≈ 0.50)
     • 🎯 valence excellent match (0.42 ≈ 0.50)
     • 🎯 acousticness excellent match (0.72 ≈ 0.50)
     • ⚠️ mood mismatch (melancholic ≠ calm)

======================================================================
```

**Analysis**: The Chill Lofi profile maintains its healthy clustering behavior (5.68-5.70, 72%) for the three lofi songs, now all showing mood mismatches due to the new -0.5 mood penalty. Even with this penalty, these songs still dominate recommendations because the genre match (+2.3) and tight energy/feature alignment outweigh the penalty. This shows the system correctly prioritizes genre-matched songs while still allowing cross-genre discovery when feature alignment is strong.

---

### Profile 3: Deep Intense Rock Listener
**Preferences**: `genre=rock, mood=intense, energy=0.85`  
**Context**: Heavy, powerful rock music with strong emotions

```
======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Storm Runner - Voltline
   Score: 7.18/7.9 │███████████████████████████░░░│ 91%
   Why you'll love it:
     • 🎯 energy excellent match (0.91 ≈ 0.85)
     • 🎯 danceability excellent match (0.66 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • ✓ acousticness good match (0.10)
     • 🎭 mood matches (intense)
     • 🎸 genre matches (rock)

----------------------------------------------------------------------

2. Dancehall Energy - Kingston Sound
   Score: 4.73/7.9 │█████████████████░░░░░░░░░░░░░│ 60%
   Why you'll love it:
     • 🎯 energy excellent match (0.86 ≈ 0.85)
     • ✓ danceability good match (0.89)
     • 🎯 valence excellent match (0.68 ≈ 0.50)
     • ✓ acousticness good match (0.16)
     • 🎭 mood matches (intense)

----------------------------------------------------------------------

3. Bass Drop Thunder - DJ Impulse
   Score: 4.70/7.9 │█████████████████░░░░░░░░░░░░░│ 59%
   Why you'll love it:
     • 🎯 energy excellent match (0.95 ≈ 0.85)
     • ✓ danceability good match (0.91)
     • 🎯 valence excellent match (0.65 ≈ 0.50)
     • ✓ acousticness good match (0.12)
     • 🎭 mood matches (intense)

----------------------------------------------------------------------

4. Neon Mambo - Havana Nights
   Score: 4.70/7.9 │█████████████████░░░░░░░░░░░░░│ 59%
   Why you'll love it:
     • 🎯 energy excellent match (0.89 ≈ 0.85)
     • ✓ danceability good match (0.88)
     • 🎯 valence excellent match (0.72 ≈ 0.50)
     • ✓ acousticness good match (0.09)
     • 🎭 mood matches (intense)

----------------------------------------------------------------------

5. Gym Hero - Max Pulse
   Score: 4.65/7.9 │█████████████████░░░░░░░░░░░░░│ 59%
   Why you'll love it:
     • 🎯 energy excellent match (0.93 ≈ 0.85)
     • ✓ danceability good match (0.88)
     • 🎯 valence excellent match (0.77 ≈ 0.50)
     • ✓ acousticness good match (0.05)
     • 🎭 mood matches (intense)

======================================================================
```

**Analysis**: The Deep Intense Rock profile shows "Storm Runner" maintaining its strong #1 position (7.18/7.9, 91%) with the improved genre weight and mood matching. The remaining songs still lack genre match but maintain good scores (4.65-4.73) due to strong mood and energy alignment. The genre cliff persists because the dataset only contains one rock song, but is somewhat mitigated by the improved weights. This demonstrates a key insight: the scoring algorithm is sound, but dataset diversity is the limiting factor for secondary recommendations.

---

## Adversarial Testing: Edge Cases & Robustness

To ensure the recommender system is robust, we tested it with four **adversarial/edge-case profiles** designed to expose potential weaknesses or unexpected behavior. These profiles test how the system handles conflicting preferences, extreme values, and non-standard mood categories.

### Test 1: Contradictory Preferences
**Profile**: `genre=rock, mood=happy, energy=0.1`  
**Challenge**: Can the system handle conflicting signals—rock (intense) with happy mood (upbeat) and very low energy (chill)?

```
📊 ADVERSARIAL PROFILE: Contradictory Preferences
   Description: Conflicting preferences: happy mood + rock genre + very low energy
   Preferences: {'genre': 'rock', 'mood': 'happy', 'energy': 0.1}

======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Storm Runner - Voltline
   Score: 5.10/7.9 │███████████████████░░░░░░░░░░░│ 65%
   Why you'll love it:
     • 🎯 danceability excellent match (0.66 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • ✓ acousticness good match (0.10)
     • ⚠️ mood mismatch (intense ≠ happy)
     • 🎸 genre matches (rock)

----------------------------------------------------------------------

2. Rooftop Lights - Indigo Parade
   Score: 4.35/7.9 │████████████████░░░░░░░░░░░░░░│ 55%
   Why you'll love it:
     • 🎯 danceability excellent match (0.82 ≈ 0.50)
     • 🎯 valence excellent match (0.81 ≈ 0.50)
     • 🎯 acousticness excellent match (0.35 ≈ 0.50)
     • 🎭 mood matches (happy)

----------------------------------------------------------------------

3. Sunrise City - Neon Echo
   Score: 4.25/7.9 │████████████████░░░░░░░░░░░░░░│ 54%
   Why you'll love it:
     • 🎯 danceability excellent match (0.79 ≈ 0.50)
     • ✓ valence good match (0.84)
     • 🎯 acousticness excellent match (0.18 ≈ 0.50)
     • 🎭 mood matches (happy)

----------------------------------------------------------------------

4. Whispers in the Rain - Indie Soul
   Score: 3.38/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.35 ≈ 0.10)
     • 🎯 danceability excellent match (0.54 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • 🎯 acousticness excellent match (0.78 ≈ 0.50)
     • ⚠️ mood mismatch (melancholic ≠ happy)

----------------------------------------------------------------------

5. Midnight Coding - LoRoom
   Score: 3.34/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 42%
   Why you'll love it:
     • 🎯 energy excellent match (0.42 ≈ 0.10)
     • 🎯 danceability excellent match (0.62 ≈ 0.50)
     • 🎯 valence excellent match (0.56 ≈ 0.50)
     • 🎯 acousticness excellent match (0.71 ≈ 0.50)
     • ⚠️ mood mismatch (chill ≠ happy)

======================================================================
```

**Finding**: With the improved weights, the system now handles contradictory preferences better. Storm Runner still scores highest (5.10) due to genre match, but the mood mismatch penalty is now visible. Items #2-3 still score well by prioritizing mood and valence over genre. The new -0.5 mood penalty makes the trade-offs more explicit to users, showing the system is considering their contradictory inputs.

---

### Test 2: Extremely Picky (All Extremes)
**Profile**: `genre=jazz, mood=sad, energy=0.95`  
**Challenge**: Can the system handle an extreme energy preference (0.95 = very high) combined with a sad mood and a rare genre (jazz)?

```
📊 ADVERSARIAL PROFILE: Extremely Picky (All Extremes)
   Description: Extreme energy (0.95) with sad mood and rare jazz genre
   Preferences: {'genre': 'jazz', 'mood': 'sad', 'energy': 0.95}

======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Coffee Shop Stories - Slow Stereo
   Score: 5.33/7.9 │████████████████████░░░░░░░░░░│ 67%
   Why you'll love it:
     • ✓ energy good match (0.37)
     • 🎯 danceability excellent match (0.54 ≈ 0.50)
     • 🎯 valence excellent match (0.71 ≈ 0.50)
     • ✓ acousticness good match (0.89)
     • ⚠️ mood mismatch (relaxed ≠ sad)
     • 🎸 genre matches (jazz)

----------------------------------------------------------------------

2. Storm Runner - Voltline
   Score: 3.38/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 43%
   Why you'll love it:
     • 🎯 energy excellent match (0.91 ≈ 0.95)
     • 🎯 danceability excellent match (0.66 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • ✓ acousticness good match (0.10)
     • ⚠️ mood mismatch (intense ≠ sad)

----------------------------------------------------------------------

3. Night Drive Loop - Neon Echo
   Score: 3.35/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 42%
   Why you'll love it:
     • 🎯 energy excellent match (0.75 ≈ 0.95)
     • 🎯 danceability excellent match (0.73 ≈ 0.50)
     • 🎯 valence excellent match (0.49 ≈ 0.50)
     • 🎯 acousticness excellent match (0.22 ≈ 0.50)
     • ⚠️ mood mismatch (moody ≠ sad)

----------------------------------------------------------------------

4. Neon Nights - Synthwave Masters
   Score: 3.34/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 42%
   Why you'll love it:
     • 🎯 energy excellent match (0.81 ≈ 0.95)
     • 🎯 danceability excellent match (0.76 ≈ 0.50)
     • 🎯 valence excellent match (0.51 ≈ 0.50)
     • 🎯 acousticness excellent match (0.19 ≈ 0.50)
     • ⚠️ mood mismatch (moody ≠ sad)

----------------------------------------------------------------------

5. Rising Sun - Trap Collective
   Score: 3.31/7.9 │████████████░░░░░░░░░░░░░░░░░░│ 42%
   Why you'll love it:
     • 🎯 energy excellent match (0.72 ≈ 0.95)
     • 🎯 danceability excellent match (0.71 ≈ 0.50)
     • 🎯 valence excellent match (0.74 ≈ 0.50)
     • 🎯 acousticness excellent match (0.31 ≈ 0.50)
     • ⚠️ mood mismatch (uplifting ≠ sad)

======================================================================
```

**Finding**: With improved weights, "Coffee Shop Stories" still dominates (#1, 5.33) as the only jazz match, even with terrible energy alignment (0.37 vs 0.95). However, the new -0.5 mood penalty is now visible on all recommendations, making the trade-offs transparent. Items #2-5 now have lower scores due to both genre mismatch AND mood penalty, showing the system appropriately discourages both categorical mismatches. Genre still dominates, but mood mismatches are now explicitly penalized.

---

### Test 3: Impossible Combo
**Profile**: `genre=lofi, mood=intense, energy=0.9`  
**Challenge**: Lofi is inherently chill (low energy), but this profile requests high-energy intense lofi—a genre/mood mismatch.

```
📊 ADVERSARIAL PROFILE: Impossible Combo
   Description: High-energy intense lofi (lofi is typically chill, not intense)
   Preferences: {'genre': 'lofi', 'mood': 'intense', 'energy': 0.9}

======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Midnight Coding - LoRoom
   Score: 5.51/7.9 │████████████████████░░░░░░░░░░│ 70%
   Why you'll love it:
     • ✓ energy good match (0.42)
     • 🎯 danceability excellent match (0.62 ≈ 0.50)
     • 🎯 valence excellent match (0.56 ≈ 0.50)
     • 🎯 acousticness excellent match (0.71 ≈ 0.50)
     • ⚠️ mood mismatch (chill ≠ intense)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

2. Focus Flow - LoRoom
   Score: 5.47/7.9 │████████████████████░░░░░░░░░░│ 69%
   Why you'll love it:
     • ✓ energy good match (0.40)
     • 🎯 danceability excellent match (0.60 ≈ 0.50)
     • 🎯 valence excellent match (0.59 ≈ 0.50)
     • 🎯 acousticness excellent match (0.78 ≈ 0.50)
     • ⚠️ mood mismatch (focused ≠ intense)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

3. Library Rain - Paper Lanterns
   Score: 5.40/7.9 │████████████████████░░░░░░░░░░│ 68%
   Why you'll love it:
     • ✓ energy good match (0.35)
     • 🎯 danceability excellent match (0.58 ≈ 0.50)
     • 🎯 valence excellent match (0.60 ≈ 0.50)
     • ✓ acousticness good match (0.86)
     • ⚠️ mood mismatch (chill ≠ intense)
     • 🎸 genre matches (lofi)

----------------------------------------------------------------------

4. Storm Runner - Voltline
   Score: 4.88/7.9 │██████████████████░░░░░░░░░░░░│ 62%
   Why you'll love it:
     • 🎯 energy excellent match (0.91 ≈ 0.90)
     • 🎯 danceability excellent match (0.66 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • ✓ acousticness good match (0.10)
     • 🎭 mood matches (intense)

----------------------------------------------------------------------

5. Dancehall Energy - Kingston Sound
   Score: 4.73/7.9 │█████████████████░░░░░░░░░░░░░│ 60%
   Why you'll love it:
     • 🎯 energy excellent match (0.86 ≈ 0.90)
     • ✓ danceability good match (0.89)
     • 🎯 valence excellent match (0.68 ≈ 0.50)
     • ✓ acousticness good match (0.16)
     • 🎭 mood matches (intense)

======================================================================
```

**Finding**: The system still strongly recommends lofi songs (5.40-5.51, 68-70%) despite major misalignment: lofi songs have energy 0.35-0.42 when the user wants 0.9, and they have wrong moods (chill/focused vs intense). However, with the new weights, the mood mismatches are now explicit (-0.5 penalty visible). Genre weight (2.3) still outweighs the combined energy + mood mismatch, which is appropriate for a user prioritizing genre consistency. This shows the system is working as designed: genre is the primary filter, with feature matching within that genre.

---

### Test 4: Niche Mood (Reflective)
**Profile**: `genre=pop, mood=reflective, energy=0.5`  
**Challenge**: "Reflective" is not a standard mood in the catalog (which has happy, calm, sad, intense). How does the system degrade when mood doesn't exist?

```
📊 ADVERSARIAL PROFILE: Niche Mood (Reflective)
   Description: Non-standard mood 'reflective' (system may not have this mood in catalog)
   Preferences: {'genre': 'pop', 'mood': 'reflective', 'energy': 0.5}

======================================================================
🎵  TOP RECOMMENDATIONS (5 songs)
======================================================================

1. Sunrise City - Neon Echo
   Score: 5.42/7.9 │████████████████████░░░░░░░░░░│ 69%
   Why you'll love it:
     • 🎯 energy excellent match (0.82 ≈ 0.50)
     • 🎯 danceability excellent match (0.79 ≈ 0.50)
     • ✓ valence good match (0.84)
     • 🎯 acousticness excellent match (0.18 ≈ 0.50)
     • ⚠️ mood mismatch (happy ≠ reflective)
     • 🎸 genre matches (pop)

----------------------------------------------------------------------

2. Gym Hero - Max Pulse
   Score: 5.26/7.9 │███████████████████░░░░░░░░░░░│ 67%
   Why you'll love it:
     • ✓ energy good match (0.93)
     • ✓ danceability good match (0.88)
     • 🎯 valence excellent match (0.77 ≈ 0.50)
     • ✓ acousticness good match (0.05)
     • ⚠️ mood mismatch (intense ≠ reflective)
     • 🎸 genre matches (pop)

----------------------------------------------------------------------

3. Jazz Blue - New York Trio
   Score: 3.47/7.9 │█████████████░░░░░░░░░░░░░░░░░│ 44%
   Why you'll love it:
     • 🎯 energy excellent match (0.52 ≈ 0.50)
     • 🎯 danceability excellent match (0.58 ≈ 0.50)
     • 🎯 valence excellent match (0.48 ≈ 0.50)
     • 🎯 acousticness excellent match (0.68 ≈ 0.50)
     • ⚠️ mood mismatch (introspective ≠ reflective)

----------------------------------------------------------------------

4. Midnight Coding - LoRoom
   Score: 3.45/7.9 │█████████████░░░░░░░░░░░░░░░░░│ 44%
   Why you'll love it:
     • 🎯 energy excellent match (0.42 ≈ 0.50)
     • 🎯 danceability excellent match (0.62 ≈ 0.50)
     • 🎯 valence excellent match (0.56 ≈ 0.50)
     • 🎯 acousticness excellent match (0.71 ≈ 0.50)
     • ⚠️ mood mismatch (chill ≠ reflective)

----------------------------------------------------------------------

5. Midnight Melancholy - Blue Notes Trio
   Score: 3.44/7.9 │█████████████░░░░░░░░░░░░░░░░░│ 44%
   Why you'll love it:
     • 🎯 energy excellent match (0.45 ≈ 0.50)
     • 🎯 danceability excellent match (0.64 ≈ 0.50)
     • 🎯 valence excellent match (0.42 ≈ 0.50)
     • 🎯 acousticness excellent match (0.72 ≈ 0.50)
     • ⚠️ mood mismatch (melancholic ≠ reflective)

======================================================================
```

**Finding**: With the improved weights, when mood "reflective" doesn't exist in the catalog, the system now **explicitly shows mood mismatches** (-0.5 penalty) on every recommendation. Pop songs (#1, #2) still dominate (5.42, 5.26) due to genre match, but the new transparency makes it clear to the user: "you requested a mood we don't have, and here's how much that's costing you." This is better than silent failure—users can see the trade-off and adjust their preferences accordingly.

---

## System Findings & Insights

### Summary of Key Observations

Across the seven test profiles (3 standard + 4 adversarial), the system revealed several consistent patterns:

1. **Genre Weight Dominates Everything** (2.0 / 7.8 = 25.6% of max score)
   - Songs matching the requested genre get massive boosts, even when other preferences are violated.
   - Example: Test 2 (Extremely Picky) recommends "Coffee Shop Stories" (5.67 score) with energy 0.37 when the user wants 0.95, simply because it's jazz.
   - Example: Test 3 (Impossible Combo) recommends lofi songs with energy 0.4 when the user wants 0.9, purely for genre matching.
   - **Implication**: The system is conservative—it filters by genre first, then tunes by features. This works for familiar genres but fails when users want cross-genre discovery.

2. **Energy Mismatches Are Forgiving**
   - The Gaussian similarity function with k=0.5 rewards "close-but-not-exact" energy matches heavily.
   - Example: Test 2 has a 0.58-point energy gap (0.95 target vs 0.37 actual) but still scores 5.67/7.8.
   - Example: Test 3 has a 0.5-point energy gap (0.9 target vs 0.4 actual) but scores 5.87/7.8.
   - **Implication**: Energy preferences are suggestions, not requirements. Good for serendipity, bad for users with strict energy needs.

3. **Mood Matching is Binary (All-or-Nothing)**
   - Exact mood matches add 1.0 point; non-matches add 0.0.
   - Example: Test 4 (Niche Mood) loses 1.0 points because "reflective" mood doesn't exist in the catalog.
   - **Implication**: Mood categories need to be curated and consistent. Semantically similar moods (calm, chill, relaxing) are treated as completely different.

4. **High-Ranked Songs Often Lack Expected Features**
   - Even in standard profiles, top-ranked songs sometimes miss mood or valence alignment.
   - Example: Profile 1 (High-Energy Pop) has #2 (Gym Hero) with no explicit mood match, and #4-5 with no genre or mood match.
   - **Implication**: The algorithm is lenient—genre + energy alignment can overcome missing mood/valence. This allows discovery but may surprise users.

5. **Catalog Size Matters**
   - With only 30 songs, there's limited diversity. If you want jazz with energy 0.95, only one song matches the genre.
   - **Implication**: Results would change dramatically with more songs. Biases might amplify or diminish depending on genre distribution.

### When the System Works Well

- **Clear, standard preferences**: If a user says "pop, happy, high energy," the system finds great matches.
- **Genre-centric users**: Users who prioritize genre first will be satisfied.
- **Feature-balanced catalogs**: If your song catalog is well-distributed across moods/energy, recommendations are diverse.

### When the System Struggles

- **Conflicting preferences**: "rock + happy + low energy" causes the system to compromise in suboptimal ways.
- **Rare genres with extreme features**: If you want a rare genre with non-typical audio features, you'll get poor matches.
- **Non-existent moods**: If the user's mood isn't in the catalog, the system silently loses 1.0 points per song.
- **Cross-genre discovery**: The heavy genre weight prevents exploring songs outside the favorite genre.

---

## Extending the Evaluation

### How to Add Your Own Profiles

You can easily add new user profiles to test different scenarios:

**1. For standard profiles**, edit `src/main.py`:
```python
user_profiles = {
    "Your Profile Name": {
        "genre": "your_genre",
        "mood": "your_mood",
        "energy": 0.5,  # 0.0 to 1.0
        "description": "Your profile description"
    },
    # ... more profiles
}
```

**2. For adversarial/edge-case profiles**, edit `src/adversarial_test.py`:
```python
adversarial_profiles = {
    "Your Edge Case": {
        "genre": "genre",
        "mood": "mood",
        "energy": 0.5,
        "description": "What are you testing?"
    },
    # ... more profiles
}
```

**3. Run your profiles**:
```bash
python -m src.main              # For standard profiles
python src/adversarial_test.py  # For adversarial profiles
```

### Profile Design Tips

- **Standard profiles** should represent real user archetypes (e.g., "Morning Workout", "Late Night Study")
- **Adversarial profiles** should challenge the system (e.g., conflicting values, rare genres, extreme feature values)
- Always include a `description` field explaining the profile's purpose
- Vary the `energy` (0.0 = low, 1.0 = high) and `mood` values to test different scenarios

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users
- Results from the standard profile evaluation (see System Evaluation section above)
- Results from the adversarial testing suite (see Adversarial Testing section above)

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read the [**Model Card**](model_card.md) for a full analysis of system behavior, biases, and evaluation results.

### Personal Engineering Reflection

**Biggest Learning Moment**: The moment I ran sensitivity testing and discovered that doubling energy weight brought "Storm Runner" (a rock song) back into pop recommendations was revelatory. Before that, I thought our weight choices were arbitrary—more genre weight was just "a good idea." But the experiment proved the opposite: the weights are *necessary solutions* to specific problems. Doubling energy from 1.2 → 2.4 reintroduced the exact contamination we'd fixed by increasing genre weight from 2.0 → 2.3. This taught me that optimization isn't about finding "the best" weights—it's about finding the *trade-offs* that matter and making deliberate choices. You can't maximize both genre coherence AND cross-genre discovery with the same weights. Every design choice is a bet on what users care about most.

**How AI Tools Helped (and When to Verify)**: Claude helped me think through the math, organize the experimental design, and articulate findings in clear language. But I had to double-check three things: (1) the sensitivity test math—I manually validated that the new max_score (7.45) was correct when we changed weights. (2) The profile comparisons—I ran the actual code to see real scores instead of trusting my intuition about how songs would rank. (3) The "Gym Hero" explanation—I had to manually trace through the scoring formula to confirm that a song with the "wrong" mood could still rank #2 when other features aligned. The pattern I noticed: AI is great at helping you think broadly and write clearly, but you *must* verify any specific numerical claims by running the actual code.

**What Surprised Me About Simple Algorithms**: The most shocking discovery was that transparency matters more than I expected. "Gym Hero" is objectively worse for a "happy pop" listener—it has the wrong mood. But when you show the math ("you're getting 85% of what you asked for"), users accept it. A user can understand: "Genre is crucial, so +2.3. Energy is nearly perfect, so +1.2. Mood doesn't match, so −0.5." That's 3.0 base points before other features, and it lands the song in top-5. The simplicity of the algorithm—just weighted features and a bell curve—somehow *feels* intelligent because the explanations are honest. Real recommender systems hide their reasoning (Netflix, Spotify, YouTube), which makes wrong recommendations feel arbitrary. Ours feels fair because you can see the math.

**What I'd Try Next**: (1) **Semantic genre similarity** using embeddings—so synthwave gets partial credit for being similar to synth pop. Right now, genre matching is all-or-nothing, which locks users into one sound. (2) **Mood embeddings** to handle "reflective" ≈ "calm"—I noticed rare moods disappear entirely because users can't describe them precisely. (3) **Behavioral signals** like skip rates—the system right now only knows what users say they like, not what they actually play. A third experiment would be A/B testing with real users to see if the mood penalty (−0.5) actually makes recommendations feel better, or if it just manipulates the math. The biggest risk in building recommenders is that you optimize for metrics (genre coherence, score diversity) that don't match what users actually want.

---
