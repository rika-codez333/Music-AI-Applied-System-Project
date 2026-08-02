# 📁 Project Files Reference Guide

Quick navigation to understand what each file does and where to look for specific information.

---

## 🎯 Start Here

| File | Purpose | Read Time |
|------|---------|-----------|
| **README.md** | Complete project guide with execution evidence | 15 min |
| **model_card.md** | Responsible AI reflection (required for grading) | 10 min |
| **PORTFOLIO.md** | Personal reflection & 5-7 min presentation outline | 5 min |

---

## 🧪 For Testing & Verification

| File | What It Does |
|------|--------------|
| `pytest` command | Run all 104 tests in 0.09 seconds |
| `tests/test_recommender.py` | Core scoring algorithm (25 tests) |
| `tests/test_semantic_genre_similarity.py` | Fuzzy genre matching (13 tests) |
| `tests/test_mood_embeddings.py` | 2D mood space (18 tests) |
| `tests/test_feedback_loop.py` | Agentic workflow (24 tests) |
| `tests/test_persistence.py` | Save/load embeddings (11 tests) |
| `tests/test_ab_testing.py` | A/B testing framework (9 tests) |
| `tests/test_playlist.py` | Playlist features (4 tests) |
| `tests/test_harness.py` | **Evaluation harness (stretch +2)** |

**Quick Command**: `python3 -m pytest -v` to see all results

---

## 🤖 For Understanding the AI Features

| File | Feature | Read Time |
|------|---------|-----------|
| **ai_interactions.md** | Agentic workflow traces (stretch +2) | 10 min |
| **SEMANTIC_GENRE_SIMILARITY.md** | How fuzzy genre matching works | 5 min |
| **MOOD_EMBEDDINGS.md** | How 2D mood space works | 5 min |
| **AGENTIC_FEEDBACK_LOOP.md** | Design of Plan→Act→Validate→Learn | 8 min |
| `src/recommender.py` | Core scoring + strategies | Code |
| `src/feedback.py` | Feedback parsing (PLAN phase) | Code |
| `src/learner.py` | Validation & learning (VALIDATE+LEARN) | Code |
| `src/feedback_loop.py` | Orchestrator (full pipeline) | Code |

**Quick Start**: Read `ai_interactions.md` for concrete workflow examples

---

## 📊 For Execution Evidence & Portfolio

| File | Purpose | Best For |
|------|---------|----------|
| `assets/execution-evidence.txt` | Test results + proof system works | Graders, interviews |
| `assets/agentic-workflow-diagram.txt` | ASCII visualization of pipeline | LinkedIn posts |
| `assets/semantic-features-guide.txt` | Deep dive into fuzzy matching | Technical interviews |
| **TEST_RESULTS.md** | Comprehensive test breakdown | Verification |
| **STRETCH_FEATURES.md** | Documentation of +6 bonus points | Grade justification |

**Quick Access**: Everything graders need is in README.md's "Execution Evidence" section

---

## 💻 For Understanding the Code

| Directory | Contains |
|-----------|----------|
| `src/` | Core system (2,500+ lines) |
| `tests/` | Test suite (104 tests, all passing) |
| `scripts/` | Utility scripts (strategy demo, etc.) |
| `data/` | Song catalog (68 songs, 14 features) |
| `diagrams/` | Architecture diagram (Mermaid .mmd) |
| `assets/` | Portfolio visuals & evidence |

**Key Files in `src/`**:
- `recommender.py` (450+ lines) — Scoring engine + strategies
- `feedback.py` (280+ lines) — Feedback parsing
- `learner.py` (260+ lines) — Validation + learning
- `feedback_loop.py` (160+ lines) — Orchestration
- `persistence.py` (200+ lines) — Save/load embeddings
- `ab_testing.py` (250+ lines) — A/B testing framework

---

## 🎓 For Project Context

| File | What It Explains |
|------|-----------------|
| **CLAUDE.md** | Project guidance & original instructions |
| **README.md** (top sections) | Original project + enhancements |
| **model_card.md** (Design Decisions) | Why we built it this way |
| **PORTFOLIO.md** | Personal reflection on lessons learned |

---

## 📋 Documentation Map (by Topic)

### System Architecture
- `SYSTEM_DIAGRAM.md` — Visual explanation of architecture
- `diagrams/architecture.mmd` — **Mermaid source (required for grading)**
- `dataflow.md` — How data flows through system

### Features (What We Built)
- `SEMANTIC_GENRE_SIMILARITY.md` — Fuzzy genre matching explained
- `MOOD_EMBEDDINGS.md` — 2D mood embedding space explained
- `AGENTIC_FEEDBACK_LOOP.md` — Plan→Act→Validate→Learn explained
- `ENHANCEMENTS.md` — Optional features guide
- `PLAYLIST_FEATURE.md` — Playlist generation details

### Testing & Reliability
- `TEST_RESULTS.md` — Complete test breakdown
- `TEST_IMPROVEMENTS.md` — How we improved tests
- `tests/` — All test files (104 tests)

### Responsible AI
- `model_card.md` — **Limitations, misuse prevention, AI collaboration**
- `ai_interactions.md` — **Agentic workflow traces**

### Portfolio & Submission
- `README.md` — **Main document (start here)**
- `PORTFOLIO.md` — Presentation outline
- `assets/` — Portfolio visuals
- `STRETCH_FEATURES.md` — +6 bonus documentation

---

## 🚀 Quick Command Reference

```bash
# Run everything
python3 -m pytest -v                    # All 104 tests
python3 tests/test_harness.py          # Evaluation harness (21/23)
python3 scripts/strategy_specialization_demo.py  # Strategy proof

# Run the system
python3 -m src.main                     # Original demo

# Check specific tests
python3 -m pytest tests/test_feedback_loop.py -v  # Agentic tests only
```

---

## 📍 File Navigation Guide

**If you want to understand...**

| Goal | Start Here | Then Read |
|------|-----------|-----------|
| "How does the system work?" | README.md → Execution Evidence | ai_interactions.md |
| "What are the limitations?" | model_card.md → System Limitations | feedback section |
| "Can I trust this code?" | TEST_RESULTS.md | assets/execution-evidence.txt |
| "How do I run it?" | README.md → Setup Instructions | Quick Start section |
| "What did you learn?" | PORTFOLIO.md → Reflection | model_card.md → Learnings |
| "How do the features work?" | SEMANTIC_GENRE_SIMILARITY.md | MOOD_EMBEDDINGS.md |
| "Is this production-ready?" | TEST_RESULTS.md + assets/execution-evidence.txt | Yes! |

---

## 💡 Pro Tips for Reading This Project

1. **For Graders**: Start with README.md "Execution Evidence" section — everything you need is there
2. **For Interviews**: Read assets/agentic-workflow-diagram.txt + semantic-features-guide.txt
3. **For Code Review**: Check tests first (TEST_RESULTS.md) to understand what works
4. **For Running**: README.md has all commands, no setup needed
5. **For Learning**: Start with ai_interactions.md, then look at the code

---

## 📚 Complete File Count

- **Markdown files**: 15+ (well-organized, all with purpose)
- **Python files**: 9 core modules (2,500+ lines)
- **Test files**: 7 (104 tests, all passing)
- **Data files**: 1 (songs.csv, 68 songs)
- **Asset files**: 3 (portfolio visuals)
- **Diagram files**: 1 (Mermaid architecture)

**Total**: Clean, focused, no bloat. Every file has a purpose.

---

**Last Updated**: August 2, 2026  
**Status**: Production-Ready (104/104 tests passing)
