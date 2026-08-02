# Portfolio Artifact: Music AI Recommender System

**Date**: August 2, 2026  
**Project**: AI110 Applied AI Systems — Music AI Recommender  
**Status**: Production-Ready (104/104 tests passing, +6 bonus points)

---

## 📌 GitHub Repository

**Repository URL**: (https://github.com/rika-codez333/Music-AI-Applied-System-Project)

**Current Project Location**: `/Users/rikaraxkz/Desktop/CodePath/AI110/Music-AI-Applied-System-Project`

**To Share**: Run these commands to push to GitHub:
```bash
git remote add origin https://github.com/[your-username]/music-ai-recommender.git
git branch -M main
git push -u origin main
```

---

## 🤖 What This Project Says About Me As An AI Engineer

**Prompt Engineering & Problem Decomposition**
This project demonstrates how I approach complex AI systems: by breaking them into testable components (PLAN→ACT→VALIDATE→LEARN) and validating each step independently before integrating. Rather than building a monolithic "smart" system and hoping it works, I designed explicit validation gates (confidence > 0.6) and conservative learning rates (0.05 = 5% per iteration) that prevent the system from degrading over time. This shows I understand that **reliability is not an afterthought—it's an architectural decision**. When Claude suggested using only SequenceMatcher for genre similarity, I tested it, found it produced 0.11 instead of expected 0.75, and pivoted to a hybrid approach. This pattern—test first, trust nothing, iterate based on evidence—reflects how I'd approach any AI system: with healthy skepticism and empirical validation.

**Semantic Understanding & Continuous Improvement**
The mood embeddings feature (mapping 17 moods to 2D semantic space where "calm" and "chill" are 0.95 similar instead of all-or-nothing) shows I can design systems that capture nuance rather than force binary classifications. The agentic feedback loop shows I understand that static systems are limited—the most interesting AI problems require *learning*. But learning has to be safe: hence the confidence thresholds that reject ambiguous feedback. This is the difference between a prototype and a production system. I can build both.

**Practical Engineering Over Academic Purity**
I chose Gaussian similarity (exp(-k×d²)) over more exotic approaches because it's interpretable and works. I used a simple 2D embedding space instead of high-dimensional vectors because it's sufficient and debuggable. When the natural language parser needed to handle edge cases, I added optional LLM enhancement with graceful degradation—Claude API fails? Fall back to pattern matching. This pragmatism matters in real systems: elegance is nice, but robustness is essential.

**Bias Detection & Responsible AI Thinking**
Model card wasn't just a checkbox—I actually identified real limitations: Western genre bias (K-pop, Bollywood underrepresented), the filter bubble risk (Gaussian scoring keeps users in preference bubbles), and the missing accessibility testing. I documented these honestly, not defensively. When I realized the system could be used for acoustic surveillance (inferring mood without consent), I specified how to prevent it (local operation, no telemetry). This shows I think about not just what the system *can* do, but what it *should* and *shouldn't* do.

**Data Structures, Testing, and Iteration**
Every key component is backed by proper data structures (FeedbackIntent, FeedbackLoopResult, EmbeddingLearner) not string-passing. The 104-test suite validates exact behavior ("genre match = +2.3 exactly") not fuzzy assertions. The test-first approach (write exact assertions, then implement) caught a critical bug immediately: the argument order in score_song(user_prefs, song) was reversed in the original tests, resulting in silent failures. TDD prevented that class of bug entirely.

**Summary**: I'm an engineer who builds AI systems with skepticism, testing, and humility. I prefer simple solutions that work over complex ones that *might* work. I think about reliability, fairness, and what could go wrong before building features. I validate claims empirically. And when I don't know something, I test it.

---

## 🎬 5-7 Minute Presentation Outline

### **INTRO (30 seconds)**
"Hi, I'm Rika. This is the Music AI Recommender System—a project that answers a real question: can we build a recommendation system that *learns* from feedback, not just predicts from fixed weights?"

**Key Insight**: Most recommenders treat preferences as fixed inputs. This one adapts.

### **PROBLEM (1 minute)**
- Original system: Static scoring (genre match = +2.3 or 0, no in-between)
- Reality: "Synthwave" is kind-of-electronic, not completely different
- Challenge: How do we make systems that:
  1. Understand nuance (genre similarity, mood embeddings)
  2. Learn from feedback safely
  3. Don't degrade over time

### **SOLUTION (2 minutes)**

**Architecture in 4 Phases:**

1. **PLAN** (Parse feedback)
   - Input: "I want something calmer"
   - Output: Intent with confidence
   - Example: energy_lower (confidence 0.92)

2. **ACT** (Adjust recommendations)
   - Apply intent to user profile
   - Original songs: Sunrise City, Seoul Pulse, Gym Hero (avg energy 0.84)
   - Adjusted: Library Rain, Midnight Coding, Focus Flow (avg energy 0.39)

3. **VALIDATE** (Check if recommendations changed)
   - Did we actually get calmer songs? YES ✓
   - How confident? 0.95 (very confident)
   - Only learn if confidence > 0.6

4. **LEARN** (Update embeddings)
   - Conservatively (5% per iteration)
   - So one bad feedback doesn't break everything

**Key Features:**
- **Semantic Similarity**: Synthwave gets 75% credit for electronic (0.75 similarity)
- **Mood Embeddings**: 2D space where calm ↔ chill = 0.95 similarity
- **Validation Gates**: Reject low-confidence feedback (prevents degradation)

### **DEMO (2-3 minutes)**

**Live Test 1: Agentic Loop Works**
```
Input: High-energy pop fan + "I want something calmer"
Output: Recommendations change from high-energy pop to lofi/calm songs
Confidence: 0.95 (very high)
Result: Embeddings updated (learning applied)
```

**Live Test 2: Safety Gate Prevents Bad Learning**
```
Input: Rock fan + "Eh, it was okay I guess"
Output: Low confidence (0.38 < 0.6 threshold)
Result: Embeddings NOT updated (system correctly rejected)
```

**Live Test 3: All Tests Pass**
```
$ python3 -m pytest -v
Result: 104/104 tests passing (100%)
```

### **IMPACT (1 minute)**

**What Works:**
- ✅ 104/104 tests passing (no regressions)
- ✅ Agentic loop stable (conservative learning prevents overfit)
- ✅ Semantic understanding (genre similarity enables cross-genre discovery)
- ✅ Reliability guardrails (confidence gates prevent degradation)

**Stretch Features (+6 bonus):**
- Agentic Workflow Enhancement: Full Plan→Act→Validate→Learn traces
- Test Harness: 23 tests with confidence scoring (91% pass rate)
- Strategy Specialization: Each strategy produces different outputs (proven)

### **LEARNING (1 minute)**

**What Surprised Me:**
1. **Simplicity Matters**: Gaussian similarity (exp(-k×d²)) outperformed fancier approaches
2. **Testing Catches Bugs**: Found argument order bug in score_song() through TDD
3. **Validation > Algorithm**: Confidence thresholds were more important than the learning algorithm itself
4. **Humility**: When Claude suggested SequenceMatcher for genre similarity, it gave 0.11 instead of 0.75—I had to pivot to a hybrid approach with an explicit relationship dictionary

**Key Insight**: Building AI isn't about being clever. It's about being skeptical, testing everything, and being willing to throw away ideas that don't work.

### **CLOSING (30 seconds)**
"This project taught me that the best AI engineers aren't the ones with the smartest ideas—they're the ones who validate their ideas, document their failures, and know when to keep things simple. That's what I've tried to show here: a system that works, that's tested, that's transparent about what it doesn't know, and that's built to improve over time."

---

## 📊 Key Metrics for Grading

| Metric | Result | Evidence |
|--------|--------|----------|
| **Core Functionality** | 104/104 tests | See README: Reproducible Execution Evidence |
| **AI Feature: Agentic Loop** | Plan→Act→Validate→Learn working | ai_interactions.md traces + tests/test_feedback_loop.py (24 tests) |
| **Semantic Understanding** | Fuzzy genre (0.75), mood embeddings (0.95) | tests/test_semantic_genre_similarity.py (13) + test_mood_embeddings.py (18) |
| **Reliability/Guardrails** | Confidence gates prevent bad learning | README Test 3 shows low-confidence feedback rejected |
| **Stretch Features** | +6 bonus (all 3 implemented) | STRETCH_FEATURES.md with full documentation |
| **Documentation** | 15+ markdown files + model card | model_card.md covers limitations, misuse prevention, surprises |
| **Reproducibility** | Commands and outputs in README | Can run tests without video/Loom |

---

## 📖 Files for Graders

**Required for Grading:**
- ✅ `README.md` — Main documentation + execution evidence
- ✅ `model_card.md` — Responsible AI reflection (limitations, misuse, collaboration)
- ✅ `ai_interactions.md` — Agentic workflow traces (stretch feature)
- ✅ `tests/test_harness.py` — Evaluation script (stretch feature)
- ✅ `scripts/strategy_specialization_demo.py` — Strategy demo (stretch feature)
- ✅ `STRETCH_FEATURES.md` — Stretch features documentation

**Recommended for Context:**
- `SYSTEM_DIAGRAM.md` — Architecture overview
- `AGENTIC_FEEDBACK_LOOP.md` — Detailed design documentation
- `TEST_RESULTS.md` — Comprehensive test results and validation
- `SEMANTIC_GENRE_SIMILARITY.md`, `MOOD_EMBEDDINGS.md` — Feature details

**Run Commands (No Video Needed):**
```bash
# Verify all tests pass
python3 -m pytest -v

# Run evaluation harness
python3 tests/test_harness.py

# Show strategy specialization
python3 scripts/strategy_specialization_demo.py
```

---
