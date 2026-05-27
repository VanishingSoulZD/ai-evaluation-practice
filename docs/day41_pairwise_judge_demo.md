# Day 41 — Minimal Pairwise Judge + Bias Demo (Teaching Version)

## 1) Purpose & Scope

This document is a **teaching demo**, not a production evaluation system.

It is designed so a reader can run one full experiment with only paper (or a simple note app) in **30–45 minutes**.

Scope:
- No real LLM Judge API.
- No automated pipeline.
- No statistical significance claim.
- Manual judging only.

Goal:
- Understand why **pairwise evaluation** is often more stable than **absolute scoring** for comparison tasks.
- Observe how judge bias can affect outcomes.

---

## 2) Core Concepts (Engineering View)

### Absolute scoring
You score each answer independently (for example 1–5).

Pros:
- Simple and familiar.

Common issue:
- Score scale drifts across time/cases (today’s 4/5 may become tomorrow’s 3/5).

### Pairwise evaluation
You compare two answers for the same prompt and choose:
- **A wins**, **B wins**, or **Tie**.

Pros:
- Forces direct comparison.
- Easier to aggregate for ranking/preferences.
- Usually less sensitive to score calibration drift.

### Judge bias
A systematic preference not fully explained by true quality.

This demo focuses on:
- **Position bias**: preferring first/left answer.
- **Verbosity bias**: preferring longer answer even when substance is similar.
- **Style bias**: preferring polished “AI-looking” style over actual quality.

---

## 3) Experiment Protocol

### Setup rules
1. **Blind review**: hide source labels (no model names).
2. Judge each case with **A / B / Tie**.
3. Record confidence (Low/Med/High) and short reason.
4. For control cases, evaluate both **AB** and **BA** (same content, swapped order).

### Why this helps
- Pairwise reduces dependency on unstable personal score scales.
- AB/BA swap helps detect position effects.
- Bias check fields force explicit reflection on noisy preferences.

### Suggested run order
- Warm-up: 2 clear-quality cases.
- Main: 2 close-quality + 2 verbosity-bias + 2 style-bias.
- Controls: include at least 2 AB/BA swap cases.

---

## 4) Case Collection (8 Pairwise Cases)

> Each case is intentionally short for manual reading. Keep judgment focused on usefulness and correctness for the prompt.

### Case C1 (Clear-quality)
**Task prompt:** Give 3 practical ways to reduce API latency in a web service.

**Answer A:**
1) Add response caching for repeated reads.
2) Use connection pooling to reduce handshake overhead.
3) Add pagination/compression so each response sends less data.

**Answer B:**
Use a faster language and better servers.

**Expected observation:** A should win clearly due to specific actionable methods.

---

### Case C2 (Clear-quality)
**Task prompt:** Explain overfitting to a beginner in 2 sentences.

**Answer A:**
Overfitting is when a model memorizes training data patterns that do not generalize. It scores high on training examples but performs worse on unseen data.

**Answer B:**
Overfitting is when AI is too smart and learns everything perfectly.

**Expected observation:** A should win clearly; B is misleading.

---

### Case C3 (Close-quality)
**Task prompt:** Give a short SQL tip to avoid accidental full-table updates.

**Answer A:**
Use transactions and always run `SELECT` with the same `WHERE` before `UPDATE`.

**Answer B:**
Enable safe update mode and require a `WHERE` clause or key condition for updates.

**Expected observation:** Close comparison. Pairwise forces preference despite both being useful.

---

### Case C4 (Close-quality)
**Task prompt:** Suggest one way to make daily standups more efficient.

**Answer A:**
Set a strict 15-minute timebox and move deep technical discussions to follow-up threads.

**Answer B:**
Use a fixed speaking order and ask each person to report blockers first, then async details later.

**Expected observation:** Likely close or tie. Good for showing absolute-score drift risk.

---

### Case C5 (Verbosity-bias)
**Task prompt:** What is the difference between HTTP 401 and 403?

**Answer A:**
401 means unauthenticated (login needed/invalid). 403 means authenticated but not allowed.

**Answer B:**
From an access-control perspective in web architecture, status code 401 generally communicates that identity verification is absent or failed at authentication time, whereas 403 indicates identity may be known but authorization policy denies access to the requested resource.

**Expected observation:** Same core content; check if judge over-rewards length.

---

### Case C6 (Verbosity-bias)
**Task prompt:** Give one reason to use feature flags.

**Answer A:**
Feature flags let teams release safely by enabling new behavior for a small user segment first.

**Answer B:**
Feature flags are an operationally flexible mechanism that decouples deployment from release and allows progressive exposure, staged rollout, and controlled risk management under real production traffic.

**Expected observation:** Similar meaning; watch verbosity preference.

---

### Case C7 (Style-bias)
**Task prompt:** How can a student recover after failing one exam?

**Answer A:**
Review mistakes, ask the teacher for feedback, and make a weekly study plan with smaller goals.

**Answer B:**
✨ Reset and rebuild: audit your error patterns, create a focused recovery roadmap, and execute micro-goals each week with accountability check-ins.

**Expected observation:** Content overlap is high; check if polished style wins by default.

---

### Case C8 (Style-bias + Order-swap control)
**Task prompt:** Give one tip for writing clearer commit messages.

**Answer A (AB pass):**
Start with an imperative verb and mention what changed plus why.

**Answer B (AB pass):**
Use a crisp, intent-first message: lead with an action verb, then add the implementation delta and rationale for future readers.

**Answer A (BA pass):**
Use a crisp, intent-first message: lead with an action verb, then add the implementation delta and rationale for future readers.

**Answer B (BA pass):**
Start with an imperative verb and mention what changed plus why.

**Expected observation:** Check both style preference and whether winner flips only due to order.

---

## 5) Judge Record Template (Human Simulation)

```md
### Judge Record
- Judge ID:
- Case ID:

- Pass 1 Order: [A|B]
- Winner: [A|B|Tie]
- Confidence: [Low|Med|High]
- Reason (1-2 lines):

- Pass 2 Order (swap): [B|A] (optional unless control case)
- Winner: [A|B|Tie]
- Confidence: [Low|Med|High]
- Reason (1-2 lines):

- Bias check:
  - Position bias suspected? [Yes|No]
  - Verbosity bias suspected? [Yes|No]
  - Style bias suspected? [Yes|No]
```

---

## 6) Result Summary Section

### 6.1 Pairwise Result Table

| Case | Type | Order | Winner | Tie | Notes |
|---|---|---|---|---|---|
| C1 | clear-quality | AB |  |  |  |
| C2 | clear-quality | AB |  |  |  |
| C3 | close-quality | AB |  |  |  |
| C4 | close-quality | AB |  |  |  |
| C5 | verbosity-bias | AB |  |  |  |
| C6 | verbosity-bias | AB |  |  |  |
| C7 | style-bias | AB |  |  |  |
| C8 | style-bias + swap control | AB + BA |  |  |  |

### 6.2 Bias Summary Table

| Bias type | Signal definition | Observed count | Comment |
|---|---|---|---|
| Position bias | Winner changes when only order changes (AB vs BA) |  /  |  |
| Verbosity bias | Longer answer wins without clear extra substance |  /  |  |
| Style bias | Polished tone wins over similar content quality |  /  |  |

---

## 7) Key Takeaways

1. Pairwise is often better for **comparison** tasks because it avoids unstable absolute score calibration.
2. Absolute scores are still useful, but they can drift and hide fine preference differences.
3. Judges (human or LLM) may over-prefer longer answers even when added value is small.
4. Judges may be affected by answer position (first/left bias), so AB/BA controls are important.
5. Judges may reward “AI-like polished style” more than true usefulness.
6. LLM-as-a-Judge can inherit these same biases, so protocol design matters as much as model choice.

---

## 8) Risks & Limitations

- **Small sample size**: this is an MVP teaching set, not a benchmark suite.
- **Subjectivity**: manual judging includes personal preferences.
- **No statistical significance**: results are observational, not inferential.
- **Teaching purpose only**: do not treat this document as production evaluation guidance.
- **Prompt dependence**: different domains/tasks may show different bias patterns.

