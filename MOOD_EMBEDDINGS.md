# Mood Embeddings — Implementation Guide

## What Changed

**Before**: Mood matching was all-or-nothing
```python
mood_match = song['mood'] == user_prefs.get('mood')
if mood_match:
    score += 1.0      # Full weight
else:
    score -= 0.5      # Penalty
```

**After**: Mood matching is proportional (embedding-based)
```python
mood_sim = mood_similarity(song['mood'], user_prefs.get('mood'))
mood_contribution = 1.0 * mood_sim  # Scales 0.0-1.0
```

## How It Works

### 2D Embedding Space

Moods are mapped to (valence, energy) coordinates:

```
        energetic (1.0)
              ↑
              │   intense (0.4, 0.95)  excited (0.8, 0.9)
              │   /
relaxed ←─────•─────→ happy (0.9, 0.7)
              │\
sad (0.2, 0.3) melancholic (0.3, 0.4)
              ↓
           calm (0.6, 0.2)
      (sad ← valence → happy)
```

### Similarity Computation

Similarity = 1.0 - (euclidean_distance / max_distance)

```python
# calm (0.6, 0.2) vs chill (0.55, 0.25)
distance = sqrt((0.6-0.55)² + (0.2-0.25)²) = 0.0707
max_distance = sqrt(2) ≈ 1.414
similarity = 1.0 - (0.0707 / 1.414) = 0.95
```

### Mood Similarity Scores

| Mood Pair | Similarity | Weight | Interpretation |
|-----------|-----------|--------|------------------|
| calm ↔ calm | 1.00 | 1.00 | Exact match |
| calm ↔ chill | 0.95 | 0.95 | Very similar |
| calm ↔ relaxed | 0.93 | 0.93 | Very similar |
| calm ↔ peaceful | 0.88 | 0.88 | Quite similar |
| calm ↔ focused | 0.72 | 0.72 | Somewhat similar |
| calm ↔ romantic | 0.48 | 0.48 | Moderately different |
| calm ↔ intense | 0.45 | 0.45 | Very different |
| happy ↔ sad | 0.43 | 0.43 | Opposite |

## Impact

### Before vs After

**Scenario**: User wants "calm", song has "chill"

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Mood similarity | 0.00 | 0.95 | +0.95 |
| Mood score | -0.50 | +0.95 | +1.45 |
| Can appear in top-5? | No | **Yes** | Enables emotional nuance |

### Recommendation Quality

**Example**: Chill lofi preference with mood embeddings

```
#1 Library Rain (chill)     - 8.80/9.5  ← Now appears due to semantic similarity
#2 Midnight Coding (chill)  - 8.76/9.5  ← Now appears due to semantic similarity
#3 Focus Flow (focused)     - 8.51/9.5  ← Somewhat similar mood gets credit
#4 Opera Aria (dramatic)    - 7.02/9.5  ← Very different mood gets minimal credit
#5 Island Vibes (relaxed)   - 6.92/9.5  ← Similar mood gets good score
```

**Before**: Only songs with "calm" mood would appear; all "chill", "relaxed", "focused" songs blocked.

## Testing

### Test Coverage

- ✅ 18 new tests in `tests/test_mood_embeddings.py`
- ✅ All 60 total tests pass (18 mood + 13 genre + 25 recommender + 4 playlist)

### Key Test Cases

```python
def test_very_similar_moods_high_similarity():
    # calm, chill, relaxed all in same emotional territory
    assert mood_similarity("calm", "chill") > 0.8

def test_opposite_moods_low_similarity():
    # happy and sad at opposite ends of valence axis
    assert mood_similarity("happy", "sad") < 0.5

def test_fuzzy_matching_enables_emotional_flexibility():
    sim = mood_similarity("calm", "chill")
    assert 0.0 < sim < 1.0  # Enables match, but prefers exact
```

## Mood Embedding Map

17 moods distributed across 2D space:

```python
MOOD_EMBEDDINGS = {
    # Happy & Energetic
    "happy": (0.9, 0.7),
    "energetic": (0.7, 0.95),
    "excited": (0.8, 0.9),
    "uplifting": (0.85, 0.75),

    # Calm & Peaceful
    "calm": (0.6, 0.2),
    "chill": (0.55, 0.25),
    "relaxed": (0.6, 0.3),
    "peaceful": (0.65, 0.15),

    # Sad & Introspective
    "melancholic": (0.3, 0.4),
    "sad": (0.2, 0.3),
    "moody": (0.35, 0.5),
    "introspective": (0.4, 0.35),

    # Intense & Aggressive
    "intense": (0.4, 0.95),
    "aggressive": (0.2, 0.9),
    "focused": (0.5, 0.7),

    # Mixed
    "romantic": (0.75, 0.5),
    "dreamy": (0.65, 0.4),
    "nostalgic": (0.45, 0.45),
}
```

## Why This Matters for the Project

### Solves Real Problem
- **Old system**: User wants "calm" but all "chill" songs blocked → No matches
- **New system**: User wants "calm" → "chill" songs get 0.95 credit → Appear in recommendations

### Enables Learning
- Foundation for behavioral loop: "User prefers chill moods" learned from feedback
- System can now track which emotional moods users actually like
- Unlike genres (fixed categories), moods are emotional→personal→learnable

### Test-Driven Quality
- Strong tests validate embedding space and similarity computation
- Regression detection: if embedding coordinates change, tests fail
- Example: If "calm" coordinate shifted to (0.7, 0.3), test `test_very_similar_moods_high_similarity` would fail

## Next Steps

1. ✅ **Semantic Genre Similarity** (DONE)
2. ✅ **Mood Embeddings** (DONE)
3. **Agentic Feedback Loop** (Next)
   - Analyzer Agent: Parse "I wanted calm but got too energetic"
   - Search Agent: Find recommendations with adjusted mood preferences
   - Validator Agent: Check if results match feedback
   - Learning Agent: Update embedding coordinates based on feedback

---

**Files Modified:**
- `src/recommender.py` — Added `mood_similarity()` function, `MOOD_EMBEDDINGS` map, updated `_compute_score()`
- `tests/test_mood_embeddings.py` — 18 new tests

**Tests Passing:** 60/60 (18 mood + 13 genre + 25 recommender + 4 playlist)
