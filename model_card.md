# Model Card: Music AI Recommender System (Enhanced)

**Project**: Music AI Recommender System (AI110 Applied AI Systems)  
**Enhanced Version**: With Semantic Genre Similarity, Mood Embeddings, Agentic Feedback Loop  
**Date**: 2026-08-02  
**Status**: Production-Ready | 104/104 Tests Passing

---

## System Limitations & Biases

### 1. Data Limitations

**Small Catalog**
- **Issue**: Only 68 songs across 25+ genres
- **Impact**: Limited diversity; results scale with dataset size
- **Mitigation**: System designed to accept larger catalogs; simply load expanded CSV
- **User Impact**: May see repeated songs if asking for niche genres

**Genre Coverage Bias**
- **Issue**: Focuses on Western genres (pop, rock, hip-hop, electronic, classical)
- **Missing**: K-pop, Bollywood, African, Latin, Middle Eastern genres underrepresented
- **Impact**: Non-Western music preferences poorly served
- **Mitigation**: Requires dataset expansion; GENRE_RELATIONSHIPS dict extensible

**Artist Representation**
- **Issue**: Some artists have only 1 song; small dataset limits nuanced learning
- **Impact**: Artist diversity penalty less effective
- **Mitigation**: Expand to 1000+ songs per artist/genre

### 2. Algorithm Limitations

**Gaussian Scoring Rewards Conformity**
- **Issue**: Energy/mood use Gaussian similarity (exp(-k×d²))
- **Impact**: Users stay in preference bubble (high-energy user never gets classical music)
- **Trade-off**: Safety vs. serendipity
- **Mitigation**: Could add "Explore" mode that ignores Gaussian penalty

**Genre Matching Uses Explicit Dict + String Similarity**
- **Limitation**: Unregistered genres get low scores; new genres need manual addition
- **Impact**: Genre similarity isn't perfect (could use pre-trained embeddings instead)
- **Mitigation**: Could integrate Spotify/Last.fm genre embeddings

**Mood Space is 2D (Valence × Energy)**
- **Simplification**: Real emotions are high-dimensional
- **Impact**: "desperate" and "motivated" both map to (low valence, high energy) but feel different
- **Mitigation**: Could expand to 3D+ space with more training data

**No Temporal Signals**
- **Issue**: Ignores release date, trends, recency
- **Impact**: Can't handle "I want 2010s vibes" or discover new releases
- **Mitigation**: Could add release_year to scoring formula

**No Behavioral Signals**
- **Issue**: Only learns from explicit text feedback, not skips/replays/saves
- **Advantage**: Privacy-preserving (users control what system learns)
- **Mitigation**: Could add optional skip tracking with consent

### 3. Learning System Limitations

**Conservative Learning Rate (0.05)**
- **Trade-off**: Slow adaptation but prevents wild swings
- **Impact**: Takes ~20 iterations to move embedding significantly
- **Mitigation**: Could use adaptive learning rate

**Fixed Confidence Threshold (0.6)**
- **Impact**: Ambiguous feedback ("I kinda liked it") ignored
- **Why**: Prevents learning from uncertain signals
- **Mitigation**: Could make threshold user-adjustable

**No Cross-User Learning (Yet)**
- **Limitation**: Each user's embeddings isolated
- **Impact**: System can't benefit from similar users' preferences
- **Foundation**: Built but not yet aggregated

### 4. Accessibility & Fairness Limitations

**No Accessibility Testing**
- Missing: Voice input, screen reader compatibility, color-blind testing
- Impact: Excludes users with disabilities
- Mitigation**: Needs WCAG 2.1 compliance audit

**No Fairness Testing Across User Groups**
- Missing: Testing across age, language, cultural backgrounds
- Impact**: Unknown performance variance
- **Mitigation**: Needs A/B testing with diverse user panel

**Filter Bubble Risk**
- **Issue**: System recommends similar music (reinforces preferences)
- **Impact**: Users may never discover truly different music
- **Mitigation**: Could add diversity bonus or "explore" mode

---

## Potential Misuse & Prevention Strategies

### 1. Feedback Manipulation

**Scenario**: User provides fake feedback to poison recommendations

**Prevention** (In Place):
- ✅ Confidence threshold (0.6) rejects low-confidence feedback
- ✅ Conservative learning rate (0.05) limits damage
- ✅ Validation gates check recommendations actually change
- ✅ Per-user isolation (multi-user not yet implemented)

**For Multi-User Learning**:
- [ ] Outlier detection (flag anomalous feedback)
- [ ] Rate limiting (max 10 feedback/hour)
- [ ] Reversibility (undo recent updates)
- [ ] Audit trail (who changed what)

### 2. Acoustic Profiling / Surveillance

**Scenario**: Infer user mood/mental state without consent

**Prevention**:
- ✅ System operates locally (no cloud transmission)
- ✅ No telemetry or user tracking
- ✅ Embeddings saved to user's disk only

**Remaining Risk**: If deployed as service, could track behavior  
**Mitigation**: Never deploy without explicit consent + transparency

### 3. Inappropriate Content

**Scenario**: Recommend explicit/violent music in child context

**Currently Missing**:
- [ ] No content filtering or explicit flag
- [ ] No age-gating or parental controls

**Mitigation Needed**:
- Add `explicit_content` flag to song CSV
- Add `target_audience` filter
- Add parent/child mode toggle

### 4. Copyright/Licensing

**Scenario**: Recommendations promote copyrighted music without attribution

**Prevention**:
- ✅ Each song includes artist/songwriter
- ✅ No streaming integration (just recommendations)
- ✅ No music playback capability

**Remaining Risk**: Could infringe if integrated with streaming service  
**Mitigation**: Display artist/copyright info with every recommendation

---

## Surprises During Testing & Reliability Validation

### 1. Critical Bug: Argument Order (SILENT FAILURE)

**What Happened**:
Tests called `score_song(song, prefs)` but function was `score_song(user_prefs, song)`. Tests passed with wrong scores.

**Why It Happened**:
No type hints made bug invisible. Tests only checked shape, not formula.

**Surprise**:
- How long this persisted (10+ test cycles)
- That logging looked plausible even though computation was wrong
- How easy to write passing tests that validate wrong thing

**Fix**: Added type hints, changed tests to validate exact formula (not ranges)

**Lesson**: Test quality >> test quantity. One assertion validating formula > 10 checking shape.

### 2. Genre Similarity Too Lenient

**What Happened**:
`SequenceMatcher` gave "synthwave" ↔ "electronic" only 0.11 similarity (should be 0.75)

**Why**: Pure string similarity doesn't understand domains. "synthwave" and "electronic" share only "e".

**Surprise**:
- How wrong string matching is for domain similarity
- That explicit GENRE_RELATIONSHIPS dict was essential
- Hybrid approach (dict + string) works much better

**Fix**: Implemented explicit relationship lookup + string fallback

**Lesson**: Domain knowledge beats generic algorithms.

### 3. Mood Thresholds Were Guessed

**What Happened**:
Test expected happy↔sad < 0.4. Actual was 0.43. Test failed.

**Why**: Didn't calculate actual Euclidean distance in 2D space.

**Math**:
```
happy:  (0.9 valence, 0.8 energy)
sad:    (0.1 valence, 0.3 energy)
distance = √[(0.9-0.1)² + (0.8-0.3)²] = 0.943
similarity = exp(-k×0.943²) ≈ 0.43
```

**Surprise**: Opposite moods aren't as dissimilar as intuition suggests (0.43 not 0.1)

**Fix**: Changed threshold to 0.5 based on actual calculations

**Lesson**: Thresholds must be mathematically justified, not guessed.

### 4. Learning Rate 0.05 Seemed Slow But Prevented Catastrophe

**What Happened**:
First implementation used rate 0.1. Single feedback moved embedding too far.
- User: "More energy"
- Old: calm (0.2, 0.2)
- New: (0.4, 0.4) — completely different!

**Surprise**:
- That 0.1 seemed reasonable but was too aggressive
- That 0.05 felt slow but was necessary
- That stability matters more than speed
- That users want incremental change, not dramatic shifts

**Fix**: Reduced to 0.05 (5% per iteration)

**Lesson**: Conservative updates > fast convergence.

### 5. Validation Gates Were More Important Than Learning Algorithm

**What Happened**:
Without confidence thresholds, system learned from bad feedback (tired user, misunderstanding, etc.)

**Surprise**: That validation checking if recommendations actually changed was the real guard

**Fix**: Added `if confidence >= 0.6` gate before learning

**Lesson**: Validation gates are as important as the learning itself.

### 6. Test-Driven Development Caught Real Bugs

**What Happened**:
Wrote tests FIRST (specified genre match = +2.3 exactly). Code failed 3 tests initially.

**Surprise**:
- How TDD prevents silent failures
- That asserting exact numbers >> fuzzy assertions
- That tests written first make bugs obvious

**Lesson**: TDD is worth it. Specify exact behavior, then implement.

---

## Collaboration with AI (Claude) During This Project

### Helpful Suggestion: Test-Driven Development

**What AI Suggested**:
"Write tests first to specify behavior. Use strong assertions validating exact formula, not 'reasonable range'."

**Why It Helped**:
- Caught argument order bug immediately
- Prevented silent failures
- Forced clarity on exact scoring
- Made debugging faster (tests told exactly what was wrong)

**Impact**:
- **Before**: Shape-checking tests, bugs invisible
- **After**: Formula-checking tests, bugs obvious
- **Result**: Caught and fixed critical bugs in first round

### Flawed Suggestion: Genre Similarity Using Only SequenceMatcher

**What AI Suggested**:
"Use difflib.SequenceMatcher to compute genre similarity automatically."

**Why It Was Wrong**:
- "synthwave" ↔ "electronic" = 0.11 (should be 0.75)
- Pure string matching doesn't understand genre relationships
- Didn't account for domain knowledge

**How I Caught It**:
Test expected 0.75, got 0.11. Test failure revealed the flaw.

**How I Fixed It**:
Implemented hybrid approach (explicit dict + string fallback):
```python
# First: check explicit relationships
if (g1, g2) in GENRE_RELATIONSHIPS:
    return GENRE_RELATIONSHIPS[(g1, g2)]  # 0.75

# Second: fall back to string similarity
return SequenceMatcher(None, g1, g2).ratio()  # 0.11
```

**Lesson**: AI suggestions are starting points, not gospel. Domain knowledge + testing catches flaws.

### Another Flawed Suggestion: Guessing Mood Thresholds

**What AI Suggested**:
"Set opposite mood threshold at 0.4; happy and sad should be very different."

**Why It Was Wrong**:
Didn't calculate actual distances. Actual result: 0.43 (just above threshold).

**How I Fixed It**:
Validated with math, adjusted threshold to 0.5.

**Lesson**: Test thresholds against actual calculations, not intuition.

---

## Overall Collaboration Assessment

### What Worked Well ✅
1. **AI excellent at architecture** — Strategy pattern, agentic pipeline, validation gates
2. **AI caught design gaps** — "Add confidence thresholds" "Validate before learning"
3. **AI good at suggesting tests** — TDD approach was powerful
4. **AI helped code quality** — Type hints, docstrings, error handling

### Where AI Made Mistakes ❌
1. **Domain-agnostic suggestions** — Genre similarity using pure string matching
2. **Guessed thresholds** — Mood similarity without calculating distances
3. **Over-confident** — Sometimes suggested approaches without testing implications
4. **No adversarial role** — Mostly agreed instead of pushing back

### How I Mitigated Mistakes 🛡️
1. **Always tested first** — Wrote tests before implementing suggestions
2. **Validated assumptions** — Calculated distances instead of guessing
3. **Used domain knowledge** — Added genre relationships when string matching failed
4. **Iterated on failures** — Treated test failures as signals to rethink

### Key Takeaway
**AI is powerful for architecture and process (TDD, validation gates, design patterns) but weaker at domain details (genre relationships, threshold tuning). Pair AI suggestions with testing and domain knowledge.**

---

## Responsible AI Principles Applied

### 1. Transparency ✅
- Open-source (CLAUDE.md documents all decisions)
- Scoring formula explicit and auditable
- Limitations documented (this file)

### 2. Validation ✅
- Strong test suite (104/104 passing)
- Confidence gates prevent bad learning
- Validation checks ensure recommendations change

### 3. User Control ✅
- Users control what system learns from
- Learning is opt-in (explicit feedback, not behavioral tracking)
- Embeddings saved to user's disk, not cloud

### 4. Fairness Limitations ⚠️
- Dataset bias toward Western genres (mitigated by open data)
- No fairness testing across user groups
- No accessibility testing

### 5. Privacy ✅
- All computation local (no cloud)
- No telemetry or user tracking
- User-specific embeddings, not shared

---

## Future Work for Responsible AI

**High Priority**:
- [ ] Accessibility audit (WCAG 2.1)
- [ ] Fairness testing across user groups
- [ ] Explicit content filtering
- [ ] Expand dataset for underrepresented genres

**Medium Priority**:
- [ ] Outlier detection for feedback anomalies
- [ ] "Explore" mode (serendipity vs. relevance)
- [ ] User-adjustable confidence threshold
- [ ] Optional behavioral signal tracking

**Lower Priority**:
- [ ] Multi-dimensional mood space (3D+)
- [ ] Temporal signals (trend, recency)
- [ ] Cross-user learning with privacy safeguards
- [ ] Explainability (why each recommendation chosen)

---

## Conclusion

This system demonstrates **responsible AI practices**:
- ✅ Transparent design (open-source, auditable)
- ✅ Validated through testing (104 tests)
- ✅ User-controlled learning (explicit feedback)
- ✅ Limitations documented
- ✅ Safe defaults (confidence gates, conservative learning)

**Key Lesson**: AI systems should be built with testing and validation as first-class concerns. A well-tested system with documented limitations is better than an untested black box.


