# Day40 BERTScore Analysis (Iteration 040)

## 1. 背景与目标

在 BLEU / ROUGE / METEOR 这类指标中，核心信号通常来自 **lexical overlap（词面重叠）**：
- 词是否一样；
- n-gram 是否命中；
- 表达是否“看起来像原句”。

这在「同义改写、语序重写、表达更自然」的生成任务中会出现偏差：
- 语义正确但用词不同，BLEU 可能很低；
- 句法变化较大时，ROUGE/METEOR 也会受影响。

因此 Iteration 040 引入 **semantic-level evaluation**：
- 从“词面匹配”扩展到“语义相似”；
- 将 BERTScore 作为 embedding-based 评测入口；
- 为后续 factual evaluation / NLI / LLM-as-a-Judge 打基础。

> 评测链路位置：Lexical metrics（BLEU/ROUGE/METEOR）→ BERTScore（semantic similarity）→ 更高阶事实与推理评测。

---

## 2. BERTScore 方法说明

### 2.1 Contextual Embeddings 是什么

BERTScore 使用上下文化表示（contextual embeddings）：
- 同一个词在不同语境中会有不同向量；
- 比起静态词向量，更能表达“词在句中含义”。

这让模型可识别：
- `boy` ↔ `child`
- `happy` ↔ `delighted`
- `bought` ↔ `purchased`

即便字面不同，也可能在语义空间中接近。

### 2.2 Token Similarity 与 Cosine Similarity

BERTScore 的核心是 token-level 语义对齐：
- candidate 中每个 token 去找 reference 中“最相近”的 token；
- 相近程度通过 **cosine similarity** 衡量；
- 再聚合为 Precision / Recall / F1。

### 2.3 Precision / Recall / F1 的意义

| 指标 | 直观含义 | 在本实验中的用途 |
|---|---|---|
| BERTScore Precision | 候选文本中的内容有多大比例能被参考语义支持 | 分析 extra noise（候选多写无关内容时 precision 常下降） |
| BERTScore Recall | 参考文本语义有多大比例被候选覆盖 | 分析 partial overlap（候选遗漏信息时 recall 常下降） |
| **BERTScore F1** | Precision 与 Recall 的综合平衡 | **主指标：bertscore_f1** |

> 本报告默认 `bertscore_f1` 为主结论指标，P/R 用于误差机制分析。

---

## 3. 实验分组设计

脚本中的 `experiment_type` 及设计目的如下：

- `exact_match`：验证上限场景，参考句与候选句完全一致。
- `semantic_similarity`：验证同义替换下的语义一致性评分能力。
- `paraphrase`：验证大幅改写（语序、句法变化）下的语义保持。
- `wording_rewrite`：验证措辞变化但语义不变时的鲁棒性。
- `semantic_contradiction`：验证语义反向（否定/反转）时指标边界。
- `factual_contradiction`：验证事实点冲突（地理/医学等）时的误判风险。
- `high_overlap_semantic_error`：验证高词面重叠但语义方向错误（polarity reversal）。
- `hallucination_like`：验证“主干正确 + 额外编造细节”的风险场景。
- `partial_overlap`：验证信息覆盖不足（省略关键信息）时 recall 变化。
- `extra_noise`：验证附加无关噪声时 precision 变化。

---

## 4. 结果总览（按组观察，而非逐行流水账）

> 当前环境下 `outputs/day40_bertscore_scores.csv` 需由脚本生成；本报告按已有实验设计与样例进行教学型分析。

### 4.1 主要组间现象

- `semantic_similarity` / `paraphrase` / `wording_rewrite`
  - 常见现象：**BERTScore F1 往往明显高于 BLEU**。
  - 解释：BLEU 依赖 exact n-gram；BERTScore 通过 contextual embedding 捕捉近义与改写。

- `semantic_contradiction` / `factual_contradiction` / `high_overlap_semantic_error`
  - 常见现象：即便语义错误，BERTScore 可能仍不低。
  - 解释：大量词面共享会抬高 token similarity，但“关键极性词”被反转。

- `hallucination_like` / `extra_noise`
  - 常见现象：候选若在正确主干上叠加额外无关内容，F1 可能不至于极低。
  - 解释：主干语义仍能匹配；但 precision 更容易受损。

- `partial_overlap`
  - 常见现象：候选太短/缺细节时 recall 更易下降。
  - 解释：参考信息未被完整覆盖。

### 4.2 与传统 lexical 指标对照

- BLEU：对同义替换和句法改写最敏感（通常偏低）。
- ROUGE：覆盖导向，能看到“提到过什么”，但不等于理解语义。
- METEOR：比 BLEU 柔和，但仍偏 lexical matching。
- **BERTScore F1**：更接近“是否在说同一件事”。

---

## 5. Semantic Similarity 深入分析

重点 case：`sem_1/sem_2/sem_3` + `para_1/para_2/para_3`

### 5.1 现象

- 这些样本里，candidate 和 reference 经常不是逐词对应：
  - 同义词替换；
  - 句法重排；
  - 局部抽象化表达。

### 5.2 原因

- lexical overlap 低：
  - BLEU n-gram 命中减少；
  - ROUGE/METEOR 也会受词形差异影响。
- semantic overlap 高：
  - contextual embeddings 可把“语义邻近词”映射到相近向量；
  - token matching 不要求字面相同。

### 5.3 机制示例

- `boy` ↔ `child`
- `happy` ↔ `delighted`
- `bought` ↔ `purchased`

这些并非字面相同，但上下文语义高度接近，因此 BERTScore 往往保持较高。

### 5.4 方法论意义

- 对于摘要、重写、问答生成等任务：
  - **BERTScore 比纯 lexical 指标更能反映 paraphrase similarity**；
  - 适合作为语义一致性的基础度量。

---

## 6. Contradiction / Hallucination 分析

重点 case：
- contradiction/factual：`contra_4`, `factual_geo_1`, `factual_med_1`, `factual_pol_1`
- hallucination/noise：`hallu_1`, `noise_1`, `noise_2`

### 6.1 semantic similarity ≠ factual correctness

- `contra_4`（否定反转）
  - 只加/改少量否定词，就能把语义翻转。
  - 许多 token 仍与 reference 相似，导致分数未必极低。

- `factual_geo_1` / `factual_med_1`
  - 仅替换核心事实 token（如地名、病原类型）即可造成事实错误；
  - 高重叠文本仍可能获得中高语义相似分。

- `factual_pol_1`
  - “reduced”→“increased”这类 polarity reversal 是典型高风险：
  - 表面相似，结论相反。

### 6.2 BERTScore 不是 hallucination detector

- `hallu_1`：主干事实正确，但追加了未被参考支持的细节。
- 结果上常见：
  - 主干匹配让分数保持不低；
  - 幻觉细节不一定被充分惩罚。

### 6.3 noise 中 precision / recall 的诊断意义

- `noise_1/noise_2`：候选加入无关噪声
  - 常见模式：**precision 下降更明显**（候选里多了不被参考支持内容）
  - recall 可能相对稳定（参考主干仍被覆盖）

> 因此 P/R 拆解是必要的：只看 F1 容易忽略“噪声型错误”。

---

## 7. 风险与局限

- BERTScore 不是 factuality metric。
- 不保证 reasoning correctness（推理链正确）。
- 不保证 hallucination detection（幻觉检测能力有限）。
- 当前是教学 demo，样本规模小，统计稳定性有限。
- 结果受 encoder/model/domain 影响（跨领域可迁移性有限）。
- 不存在可跨任务复用的通用阈值，需要本任务标定。

---

## 8. 结论

### 8.1 主结论

BERTScore 更适合评估：
- paraphrase 保真度；
- semantic similarity；
- flexible generation（表达变化大但语义一致）。

### 8.2 边界

BERTScore 不是：
- fact checker；
- verifier；
- reasoning evaluator。

### 8.3 下一步

后续完整评测应叠加：
- factual evaluation；
- NLI（蕴含/矛盾）信号；
- LLM-as-a-Judge（含可解释 rubric）。

---

## Appendix: 必看样例清单（教学推荐）

- Semantic/Paraphrase：`sem_1`, `sem_2`, `sem_3`, `para_1`, `para_2`, `para_3`
- Contradiction/Factual：`contra_4`, `factual_geo_1`, `factual_med_1`, `factual_pol_1`
- Hallucination/Noise：`hallu_1`, `noise_1`, `noise_2`
