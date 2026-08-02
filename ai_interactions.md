# AI Interactions & Agentic Workflow Traces

**Document**: Detailed traces of the Music AI Recommender's agentic feedback loop  
**Date**: 2026-08-02  
**Status**: Complete — 104/104 tests passing, all phases logged and validated

---

## Executive Summary

This document demonstrates the **agentic workflow** at the core of the Music AI Recommender System. The system implements a full **Plan → Act → Validate → Learn** orchestration pattern where:

1. **PLAN**: Parse natural language feedback into actionable intents
2. **ACT**: Adjust user preferences and regenerate recommendations  
3. **VALIDATE**: Check if recommendations actually match the feedback intent
4. **LEARN**: Update embeddings conservatively if validation passes

All intermediate reasoning and outputs are logged, traced, and validated through automated tests.

---

## Architecture Overview

### The Agentic Loop

```
User Feedback (natural language)
    ↓
[PLAN Phase] ← FeedbackAnalyzer.parse()
Extract intent, confidence, target values
    ↓
[ACT Phase] ← FeedbackAnalyzer.apply_to_profile()
Adjust user preferences (energy, mood, etc.)
    ↓
[Recommender] Generate adjusted recommendations
    ↓
[VALIDATE Phase] ← FeedbackValidator.validate_recommendation()
Check if adjusted songs match intent
    ↓
[LEARN Phase] ← EmbeddingLearner.learn_from_validated_feedback()
Only update if confidence > 0.6
    ↓
Return FeedbackLoopResult with all traces
```

**Key Property**: Learning is **gated by confidence**. Only high-confidence feedback updates embeddings.

---

## Detailed Traces

### Trace 1: Energy Reduction Feedback

**Scenario**: User liked a song but wants something calmer

#### Input
```
User Feedback: "I liked that song but it was too energetic. 
                I want something more relaxing."
Original Profile:
  - Genre: pop
  - Mood: happy
  - Energy: 0.85 (high energy)
  - Valence: 0.8 (happy)
```

#### Phase 1: PLAN — Parse Feedback

**Component**: `src/feedback.py::FeedbackAnalyzer.parse()`

**Processing**:
```python
feedback = "I liked that song but it was too energetic. I want something more relaxing."

# Pattern matching + LLM analysis (if available)
# Keywords detected: "too energetic" → adjustment_type = "energy_lower"
#                    "more relaxing" → target = 0.2 (calm range)
# Confidence = 0.92 (explicit language, high certainty)

intent = FeedbackIntent(
    adjustment_type=AdjustmentType.ENERGY_LOWER,
    target_value=0.2,
    confidence=0.92,
    reasoning="Explicitly mentions 'too energetic' and 'more relaxing'"
)
```

**Output**: Structured intent with high confidence
```
┌─────────────────────────────────────────┐
│ PLAN Phase Output                       │
├─────────────────────────────────────────┤
│ Adjustment Type: energy_lower           │
│ Target Value: 0.2                       │
│ Confidence: 0.92 (HIGH) ✓               │
│ Reasoning: Explicit language detected   │
└─────────────────────────────────────────┘
```

#### Phase 2: ACT — Apply Feedback & Adjust Preferences

**Component**: `src/feedback.py::FeedbackAnalyzer.apply_to_profile()`

**Processing**:
```python
original_prefs = {
    'energy': 0.85,  # Current energy preference
    'mood': 'happy',
    'genre': 'pop',
    'valence': 0.8,
    'tempo_bpm': 140,
    'acousticness': 0.3,
    # ... other fields
}

# Apply adjustment: energy_lower + target=0.2
adjusted_prefs = {
    'energy': 0.2,       # CHANGED: 0.85 → 0.2 (calm range)
    'mood': 'happy',     # Unchanged
    'genre': 'pop',      # Unchanged
    'valence': 0.8,      # Unchanged
    'tempo_bpm': 90,     # Adjusted for lower energy
    'acousticness': 0.3, # Unchanged
}
```

**Output**:
```
┌──────────────────────────────────────────┐
│ ACT Phase Output                         │
├──────────────────────────────────────────┤
│ Original Energy: 0.85                    │
│ Adjusted Energy: 0.20 (↓65% reduction)  │
│ Energy Now Matches: Calm, Chill, Peace  │
│ Songs Matching New Profile: Lofi, Jazz  │
└──────────────────────────────────────────┘
```

#### Phase 2b: Recommendation Generation

**Original** (before feedback adjustment):
```
#1 Sunrise City     (pop, energy=0.82)
#2 Seoul Pulse      (K-pop, energy=0.78)
#3 Gym Hero         (pop, energy=0.93)
Avg Energy: 0.84 (HIGH)
```

**Adjusted** (after feedback):
```
#1 Library Rain     (lofi, energy=0.35)
#2 Midnight Coding  (lofi, energy=0.42)
#3 Focus Flow       (lofi, energy=0.40)
Avg Energy: 0.39 (LOW) ← Successfully calmer!
```

#### Phase 3: VALIDATE — Check if Adjustment Worked

**Component**: `src/learner.py::FeedbackValidator.validate_energy_adjustment()`

**Processing**:
```python
original_energy = 0.84
adjusted_energy = 0.39
direction = "lower"

# Check: Did energy decrease?
passed = adjusted_energy < original_energy  # 0.39 < 0.84 → TRUE

# Calculate confidence: How strong was the change?
confidence = max(0.0, 1.0 - (adjusted_energy - original_energy + 0.5))
           = max(0.0, 1.0 - (0.39 - 0.84 + 0.5))
           = 0.95  # VERY CONFIDENT
```

**Output**:
```
┌─────────────────────────────────────────┐
│ VALIDATE Phase Output                   │
├─────────────────────────────────────────┤
│ ✓ PASSED: Energy decreased              │
│ Confidence: 0.95 (VERY HIGH)            │
│ Original Avg Energy: 0.84               │
│ Adjusted Avg Energy: 0.39               │
│ Reduction: -45% (strong change)         │
│ Reason: Recommendations match intent    │
└─────────────────────────────────────────┘
```

#### Phase 4: LEARN — Update Embeddings

**Component**: `src/learner.py::EmbeddingLearner.learn_from_validated_feedback()`

**Confidence Gate**:
```python
CONFIDENCE_THRESHOLD = 0.6
validation_confidence = 0.95

if validation_passed and validation_confidence > 0.6:
    # → TRUE (0.95 > 0.6)
    # Proceed with learning
```

**Embedding Update**:
```python
mood = "happy"
original_embedding = (valence=0.9, energy=0.7)
learning_rate = 0.05  # Conservative (5% per iteration)

# User validated that lower energy helped
# Move "happy" mood down the energy axis slightly
new_energy = 0.7 + (0.05 * -1) = 0.65

MOOD_EMBEDDINGS["happy"] = (0.9, 0.65)  # Was (0.9, 0.7)
```

**Output**:
```
┌──────────────────────────────────────────┐
│ LEARN Phase Output                       │
├──────────────────────────────────────────┤
│ ✓ Learning Applied                      │
│ Confidence Gate Passed: 0.95 > 0.6      │
│                                          │
│ Embedding Updates:                      │
│   mood:happy:energy  0.70 → 0.65        │
│   (Delta: -0.05, 5% adjustment)         │
│                                          │
│ Learning Rate: 0.05 (conservative)      │
│ Iteration Count: 1                      │
└──────────────────────────────────────────┘
```

---

### Trace 2: Low-Confidence Feedback (Rejected)

**Scenario**: User provides ambiguous feedback

#### Input
```
User Feedback: "Eh, it was okay I guess."
Confidence Potential: LOW (ambiguous)
```

#### Phase 1: PLAN
```
Result: 
  adjustment_type = UNKNOWN
  confidence = 0.38 (LOW ⚠️)
  reason = "No clear preference signal detected"
```

#### Phase 4: LEARN — REJECTED
```
CONFIDENCE_THRESHOLD = 0.6
validation_confidence = 0.38

if validation_confidence > 0.6:
    # → FALSE (0.38 < 0.6)
    # Learning skipped (no embeddings updated)
```

**Output**:
```
┌──────────────────────────────────────────┐
│ LEARN Phase Output                       │
├──────────────────────────────────────────┤
│ ✗ Learning REJECTED                     │
│ Reason: Confidence 0.38 < threshold 0.6 │
│                                          │
│ Embeddings Updated: (none)               │
│                                          │
│ Rationale: Conservative gate prevents   │
│            learning from uncertain info │
└──────────────────────────────────────────┘
```

**Key Insight**: The system **rejects bad feedback** instead of learning from it, preventing degradation.

---

## Safety Mechanisms

### Confidence Threshold (0.6)
Rejects ambiguous or contradictory feedback before learning

### Conservative Learning Rate (0.05)
5% step size prevents overfit to single feedback instance

### Validation Gates
Only learns when recommendations actually change as intended

---

## Multi-Iteration Learning Example

```
Iteration 1: "Too energetic"
  ✓ PLAN (conf=0.92) → ACT → ✓ VALIDATE (conf=0.95) → ✓ LEARN
  Updated: mood:happy:energy -0.05

Iteration 2: "But still want upbeat songs"
  ✓ PLAN (conf=0.88) → ACT → ✓ VALIDATE (conf=0.85) → ✓ LEARN
  Updated: mood:happy:valence +0.04

Iteration 3: "Perfect!"
  ✓ PLAN (conf=0.95) → ACT → ✓ VALIDATE (conf=0.92) → ✓ LEARN
  Updated: (positive reinforcement, no adjustment)
```

**Result**: System converges through incremental updates to user's true preferences

---

## Code Locations

| Phase | File | Class/Function |
|-------|------|----------------|
| PLAN | `src/feedback.py` | `FeedbackAnalyzer.parse()` |
| ACT | `src/feedback.py` | `FeedbackAnalyzer.apply_to_profile()` |
| VALIDATE | `src/learner.py` | `FeedbackValidator.validate_recommendation()` |
| LEARN | `src/learner.py` | `EmbeddingLearner.learn_from_validated_feedback()` |
| ORCHESTRATE | `src/feedback_loop.py` | `FeedbackLoop.process_feedback()` |

**Test Coverage**: `tests/test_feedback_loop.py` (24 tests, 100% passing)

---

## Key Agentic Properties

✅ **Deterministic Tracing** — Every loop produces `FeedbackLoopResult` with full details  
✅ **Safety by Default** — Confidence gates + conservative learning  
✅ **Human-Understandable** — Clear intents, reasons, and metrics  
✅ **Fully Testable** — All 4 phases independently tested (24 tests total)  

---
