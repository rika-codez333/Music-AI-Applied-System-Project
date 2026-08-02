# Music AI Recommender System — Claude Code Guide

## Project Overview

This is an **AI110 Applied AI Systems** project: a content-based music recommender system that predicts song recommendations based on audio features, user preferences, and multiple scoring strategies.

**Key features:**
- Gaussian-based scoring for audio feature similarity (energy, danceability, valence, tempo, acousticness)
- Multiple recommendation strategies via Strategy pattern (Genre-First, Mood-First, Energy-Focused, etc.)
- Diversity penalty logic to prevent artist/genre clustering
- Comprehensive test suite with standard and adversarial user profiles
- Interpretable explanations for every recommendation

**Tech Stack:**
- Python 3.x
- pandas, numpy for data processing
- dataclasses for type-safe data structures
- pytest for testing

## Core System Architecture

### Files & Responsibilities

| File | Purpose |
|------|---------|
| `src/recommender.py` | Core scoring engine; Strategy pattern implementations; Song/UserProfile dataclasses |
| `src/main.py` | CLI interface; recommendation display; diversity penalty application |
| `src/playlist.py` | Playlist generation and management features |
| `src/adversarial_test.py` | Edge-case testing suite (contradictory preferences, extreme values, etc.) |
| `data/songs.csv` | Song catalog (68 songs across 25+ genres with 10 attributes) |

### Scoring Algorithm (Current)

**Features scored:**
- Genre (exact match: +2.3)
- Mood (exact match: +1.0, mismatch: -0.5)
- Energy (Gaussian similarity: 1.2 × exp(-k×d²))
- Danceability (Gaussian similarity: 1.2 × exp(-k×d²))
- Valence (Gaussian similarity: 1.0 × exp(-k×d²))
- Tempo (Gaussian similarity: 0.6 × exp(-k×d²))
- Acousticness (Gaussian similarity: 0.6 × exp(-k×d²))
- Popularity (Gaussian similarity: variable by strategy)
- Production Quality (Gaussian similarity: variable by strategy)
- Artist Familiarity (Gaussian similarity: variable by strategy)

**Max score:** ~9.5 (varies by strategy)

### Known Limitations & Design Decisions

1. **Genre matching is all-or-nothing** — No semantic similarity between genres (e.g., synthwave doesn't partially match synth-pop)
2. **Mood matching is exact** — "reflective" and "introspective" are treated as completely different
3. **Gaussian scoring rewards user-preference proximity** — High-energy users never get truly low-energy songs, limiting serendipity
4. **Tiny catalog** — Only 68 songs limits diversity; results scale with dataset size
5. **No temporal signals** — System ignores release date and trending status
6. **No feedback loop** — System doesn't learn from user behavior (skips, replays)

## How to Run & Test

### Standard Evaluation
```bash
python -m src.main
```
Runs 3 diverse user profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock

### Adversarial Testing
```bash
python src/adversarial_test.py
```
Tests 4 edge cases: Contradictory preferences, Extremely Picky, Impossible Combo, Niche Mood

### Run Tests
```bash
pytest
```

## Guardrails & Safety Mechanisms

These hooks are configured in `.claude/settings.json` to prevent breaking changes:

### 🚨 Hard Stops (Block Action)
- **Tests must pass before commits** — `git commit` runs pytest and blocks if any test fails
- **Critical file deletion** — Blocks `rm` on songs.csv, recommender.py, or test files without confirmation

### ⚠️ Warnings (Confirm Intent)
- **Core algorithm changes** — Warns when editing `src/recommender.py` or `src/main.py`
- **Song catalog edits** — Warns if modifying `data/songs.csv` and checks all required columns exist
- **Test profile changes** — Warns when editing `src/adversarial_test.py` or test files (might invalidate comparisons)
- **Playlist feature edits** — Warns when modifying `src/playlist.py` (ensures Strategy pattern compliance)
- **Documentation edits** — Warns on edits to CLAUDE.md, README.md, model_card.md, ai_interactions.md
- **New file creation** — Warns when creating new files in `src/` (ensures they follow established patterns)

### ✅ Validation Hooks (Post-Edit)
- **Syntax check** — After editing `src/recommender.py`, validates Python syntax
- **CSV validation** — After editing `data/songs.csv`, verifies all required columns are present

### Feedback Integration & Test Improvements

**Addressed from feedback:**
- ✅ Fixed critical argument order bug in `score_song(user_prefs, song)` — tests were calling it backwards
- ✅ Upgraded tests from structural (checking shapes/types) to numerical (validating exact formula)
- ✅ Added strong assertions for genre weight (+2.3), mood match (+1.0), mood mismatch (-0.5)
- ✅ All 25 tests now validate correctness, not just structure

**See**: `TEST_IMPROVEMENTS.md` for detailed breakdown of what was fixed.

## Core Improvements (Assignment Focus)

Foundation for agentic music recommendation system with learning loop.

### 1. **Semantic Genre Similarity** ✅ COMPLETE
**Goal**: Allow "synthwave" to get partial credit for matching "electronic"  
**Solution**: Hybrid fuzzy matching (explicit relationships + string similarity)  
**Result**: Genre scores now 0.0-2.3 (proportional) instead of 0 or 2.3  
**Impact**: Enables cross-genre discovery while respecting preferences  
**Tests**: 13 new tests, all passing  
**See**: `SEMANTIC_GENRE_SIMILARITY.md`

### 2. **Mood Embeddings** ✅ COMPLETE
**Goal**: "calm", "chill", "relaxed" should be semantically similar  
**Solution**: 2D embedding space (valence, energy) with euclidean distance-based similarity  
**Result**: Mood scores now 0.0-1.0 (proportional) instead of -0.5 or +1.0  
**Impact**: Emotional nuance enabled; "calm" ↔ "chill" similarity = 0.95  
**Tests**: 18 new tests, all passing  
**See**: `MOOD_EMBEDDINGS.md`

### 3. **Agentic Feedback Loop** ✅ COMPLETE
**Goal**: System learns from user feedback and improves recommendations  
**Solution**: Plan → Act → Validate → Learn orchestration pattern  
**Result**: System adapts to user preferences; embeddings improve with feedback  
**Impact**: Turns static recommender into learning system  
**Tests**: 24 comprehensive tests, all passing  
**See**: `AGENTIC_FEEDBACK_LOOP.md`

## Active Experiments & Improvements

**Progress:**
- [x] Test suite improvements & bug fixes (✅ Complete)
- [x] Semantic genre similarity (✅ Complete, 13 tests)
- [x] Mood embeddings (✅ Complete, 18 tests)
- [x] Agentic feedback loop (✅ Complete, 24 tests)
- [ ] Logging & guardrails system
- [ ] Reproducible setup & documentation

**Overall Status**: All 3 core phases complete. 84/84 tests passing (60 original + 24 new feedback loop tests).

## Guidance for Claude Code

### What to prioritize

**High-impact improvements:**
1. **Semantic genre similarity** — Use embeddings or fuzzy matching so "synthwave" gets partial credit for being like "synth-pop"
2. **Mood embeddings** — Map moods to semantic space so "calm" ≈ "relaxed" ≈ "chill"
3. **Behavioral signals** — Add skip rate or replay tracking to learn from actual user behavior
4. **Cross-genre discovery** — Reduce genre weight or add diversity bonus to encourage exploration

**Medium-impact:**
5. Expand song catalog
6. Add temporal signals (recency bias)
7. A/B testing framework for strategy comparison

**Low-impact:**
8. UI/UX improvements to display
9. Config file for weight tuning

### Verification Rules

- **Always run `pytest` after changes** to ensure existing tests pass
- **Always run `python -m src.main` to see outputs change** before declaring a feature done
- **Compare before/after scores** for the same profiles to show the delta
- **Check adversarial profiles** — if one improvement breaks edge-case handling, it's not ready

### Code Style

- Type hints required (use dataclasses where possible)
- Docstrings for public functions (one-liner suffices)
- Comments only for WHY (not WHAT)
- No premature abstractions — three similar lines > one early helper
- Test-driven where possible

### Files You Own

You're encouraged to create/modify:
- `src/recommender.py` — Core algorithm tuning
- `tests/test_recommender.py` — New test cases
- `data/songs.csv` — Expand catalog or adjust features
- Experiment scripts in root (`experiment_*.py`)

Avoid changing:
- Core structure of `main.py` without discussion
- Test framework setup

---
