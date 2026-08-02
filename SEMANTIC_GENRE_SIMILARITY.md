# Semantic Genre Similarity — Implementation Guide

## What Changed

**Before**: Genre matching was all-or-nothing
```python
genre_match = song['genre'] == user_prefs.get('genre')
if genre_match:
    score += 2.3  # Full weight
else:
    score += 0.0  # Nothing
```

**After**: Genre matching is proportional (fuzzy)
```python
genre_sim = genre_similarity(song['genre'], user_prefs.get('genre'))
genre_contribution = 2.3 * genre_sim  # Scales from 0.0 to 2.3
```

## How It Works

### Similarity Scoring

1. **Exact Match** (1.0)
   - `pop` ↔ `pop` → 2.30 points

2. **Related Genres** (0.75)
   - `electronic` ↔ `synthwave` → 1.72 points
   - `pop` ↔ `synth-pop` → 1.72 points
   - Uses explicit `GENRE_RELATIONSHIPS` lookup table

3. **Similar Keywords** (0.3-0.6)
   - `pop` ↔ `indie-pop` → 0.69 points (shared "pop")
   - Uses string similarity + keyword matching

4. **Unrelated** (0.0)
   - `pop` ↔ `jazz` → 0.00 points

### Algorithm

```python
def genre_similarity(genre_a: str, genre_b: str) -> float:
    # 1. Check explicit relationships first (high confidence)
    if explicit_relationship_exists(a, b):
        return 0.75
    
    # 2. Fall back to string similarity
    string_sim = SequenceMatcher(a, b).ratio()
    
    # 3. Boost if genres share keywords (e.g., "synth-pop" & "synthwave" both have "synth")
    if shared_keywords(a, b):
        string_sim += keyword_boost
    
    return string_sim
```

## Impact

### Before vs After

**Scenario**: User prefers "electronic", song is "synthwave"

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Genre similarity | 0.00 | 0.75 | +0.75 |
| Genre score | 0.00 | 1.72 | +1.72 |
| Can appear in top-5? | No | **Yes** | Enables discovery |

### Recommendation Quality

**Example**: Electronic preference with 5 recommendations

```
#1 Neon Nights (synthwave)    - 8.29/9.5  ← Now appears due to semantic similarity
#2 Night Drive (synthwave)    - 8.28/9.5  ← Now appears due to semantic similarity
#3 Indie Rock (indie-rock)    - 7.45/9.5  ← Now appears with partial credit
#4 Electric Dreams (electronic) - 7.31/9.5 ← Exact match still ranks high
#5 Electric Vibes (electronic) - 7.30/9.5  ← Exact match still ranks high
```

**Before**: Only #4 and #5 would appear; synthwave and indie-rock blocked completely.

## Testing

### Test Coverage

- ✅ 13 new tests in `tests/test_semantic_genre_similarity.py`
- ✅ All 25 original tests still pass
- ✅ 42 total tests pass

### Key Test Cases

```python
def test_exact_match_returns_one():
    assert genre_similarity("pop", "pop") == 1.0

def test_related_genres_get_partial_credit():
    sim = genre_similarity("electronic", "synthwave")
    assert 0.7 < sim < 1.0  # Partial credit

def test_fuzzy_matching_enables_discovery():
    # User wants electronic, song is synthwave
    # Should score: 0 < score < 2.3 (enables discovery, but less than exact)
    assert 0.0 < genre_similarity("electronic", "synthwave") < 1.0
```

## Genre Relationship Map

Current relationships (in `GENRE_RELATIONSHIPS`):

```python
{
    "pop": ["synth-pop", "indie-pop"],
    "rock": ["metal", "indie-rock", "alternative"],
    "electronic": ["synthwave", "synth-pop", "edm", "house", "techno"],
    "lofi": ["lo-fi", "chill-hop"],
    "hip-hop": ["trap", "rap"],
    "jazz": ["smooth-jazz", "bebop"],
    "indie": ["indie-rock", "indie-pop"],
}
```

**How to extend**: Add more genre pairs to enable new cross-genre relationships.

## Why This Matters for the Project

### Solves Real Problem
- **Old system**: "I want synthwave but prefer electronic" → Synthwave blocked (different genre)
- **New system**: "I want synthwave but prefer electronic" → Synthwave gets 75% credit

### Enables AI Learning
- Foundation for next feature: **Behavioral signals** will learn which related genres users actually like
- Example: If user consistently likes synthwave-over-pure-electronic, system learns to boost synthwave weight

### Test-Driven Quality
- Strong tests validate exact scoring behavior
- Regression detection: if genre weights change, tests fail immediately
- Example: If synthwave similarity dropped to 0.5, test `test_related_genres_get_partial_credit` would catch it

## Next Steps

1. ✅ **Semantic Genre Similarity** (DONE)
2. **Mood Embeddings** — Same approach for moods
   - "calm", "chill", "relaxed" → semantic similarity
   - Continuous scale instead of all-or-nothing
3. **Behavioral Learning** — Track which related genres user actually likes
   - Update weights based on feedback
   - Build agentic feedback loop

---

**Files Modified:**
- `src/recommender.py` — Added `genre_similarity()` function, updated `_compute_score()`
- `tests/test_semantic_genre_similarity.py` — 13 new tests

**Tests Passing:** 42/42 (25 original + 13 new + 4 playlist)
