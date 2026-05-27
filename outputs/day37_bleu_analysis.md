# Day 37 BLEU Analysis Report

## 1. Introduction

This report explains **why BLEU changes** across experiments rather than only listing scores.
In this setup, BLEU is computed at sentence level using tokenized lowercased text (`split()`), so the metric focuses on **surface-form overlap** between candidate and reference.

BLEU is a classic **precision-oriented** metric: it emphasizes how much of the generated candidate can be matched by the reference.
It is less about whether the candidate fully covers all reference information.

---

## 2. BLEU Core Mechanisms

### 2.1 Precision-oriented

BLEU rewards candidate tokens and phrases that appear in the reference.
This means:
- generating unsupported words is penalized;
- conservative overlap is rewarded;
- but full content coverage is not directly optimized like a recall metric.

### 2.2 n-gram overlap

BLEU combines overlap across:
- **unigram (1-gram)**: word-level matching
- **bigram (2-gram)**: short phrase/order matching
- **trigram (3-gram)**: stronger local structure matching
- **4-gram**: strict phrase continuity and word-order consistency

Higher-order n-grams are much more sensitive to word order.
So two sentences with similar words can still get lower BLEU if phrase order changes.

### 2.3 Brevity penalty

BLEU includes a brevity penalty to prevent systems from outputting only short keyword fragments.
Even if a short candidate contains some correct words, it loses score because:
- many higher-order n-grams are absent;
- candidate length is too short compared with reference.

---

## 3. Experiment Analysis

### 3.1 exact_match

Average BLEU: **1.000000**

- `exact_1` BLEU=1.000000 | ref: "The cat is on the mat" | cand: "The cat is on the mat"
- `exact_2` BLEU=1.000000 | ref: "Machine translation needs careful evaluation" | cand: "Machine translation needs careful evaluation"

Interpretation:
- Candidate and reference are identical, so overlap is perfect at all n-gram orders.
- This is the easiest case for BLEU and approaches the practical upper bound.
- It shows BLEU strongly rewards literal agreement in wording and order.

### 3.2 word_order_change

Average BLEU: **0.345721**

- `order_1` BLEU=0.000000 | ref: "The cat is on the mat" | cand: "On the mat the cat is"
- `order_2` BLEU=0.691442 | ref: "I really like this natural language processing course" | cand: "This natural language processing course I really like"

Interpretation:
- Most words are preserved, so unigram overlap remains relatively strong.
- However, reordered phrasing breaks many bigram/trigram/4-gram matches.
- This causes a visible drop and demonstrates BLEU's sensitivity to local word order.

### 3.3 synonym_paraphrase

Average BLEU: **0.000000**

- `syn_1` BLEU=0.000000 | ref: "The movie was very good" | cand: "The film was really great"
- `syn_2` BLEU=0.000000 | ref: "He solved the problem quickly" | cand: "He fixed the issue rapidly"

Interpretation:
- Semantic meaning is similar, but lexical forms differ ("movie/film", "good/great", etc.).
- Because BLEU relies on exact token overlap, synonym substitutions can sharply reduce score.
- This demonstrates that BLEU does not directly capture semantic equivalence.

### 3.4 brevity_penalty

Average BLEU: **0.000000**

- `brevity_1` BLEU=0.000000 | ref: "The weather is warm and sunny today" | cand: "warm"
- `brevity_2` BLEU=0.000000 | ref: "We need a detailed and complete project report" | cand: "complete report"

Interpretation:
- Candidates keep only fragments of the reference.
- Short outputs lose score both from missing higher-order n-grams and brevity penalty.
- This shows BLEU discourages keyword-only outputs and favors sufficiently complete responses.

---

## 4. BLEU Limitations

1. **Semantic blindness**  
   BLEU matches surface forms, not deep meaning; semantically correct paraphrases may be undervalued.

2. **Paraphrase sensitivity**  
   Legitimate rewording and reordering can reduce overlap even when human quality is acceptable.

3. **Sentence-level instability**  
   Sentence BLEU can fluctuate strongly for short or stylistically varied outputs; single-sentence interpretation should be cautious.

4. **Single-reference limitation**  
   One reference cannot cover all valid phrasings, so BLEU may penalize alternative correct expressions.

---

## 5. Conclusion

BLEU is a foundational **overlap-based** metric that is useful for monitoring textual agreement with references.
However, BLEU is not equivalent to true semantic quality.
It is most reliable in tasks where phrasing is relatively constrained.

For robust evaluation, BLEU should be combined with:
- **ROUGE** (overlap from another angle),
- **BERTScore** (semantic similarity),
- **LLM Judge** (instruction-following and coherence),
- **human evaluation** (final quality grounding).
