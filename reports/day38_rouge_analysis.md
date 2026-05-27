# Day38 Task 4 — ROUGE Analysis Report (Iteration 038)

## 1. Executive Summary

### 本报告回答什么问题
- ROUGE 在自动评测中到底衡量什么，尤其是 **recall-oriented / coverage-oriented** 的意义。
- 在同一批实验里，BLEU、ROUGE-1、ROUGE-2、ROUGE-L 各自会奖励/惩罚什么行为。
- 为什么 ROUGE-L（LCS）是“词面重合”与“顺序保留”之间的重要桥梁。

### 核心结论（3~5条）
- ROUGE 的核心价值不是“表达是否一模一样”，而是“参考信息是否被覆盖”。
- BLEU 更偏 precision，ROUGE 更偏 coverage；二者是互补关系，不是替代关系。
- ROUGE-1 常用于看“信息是否被提到”，ROUGE-2 更严格，强调局部短语连续性。
- ROUGE-L 通过 LCS 反映保序性：即使词都出现，若全局顺序被打散，ROUGE-L 也会明显下降。
- 仅靠 overlap 指标会低估同义改写、并可能被关键词堆砌“投机优化”，必须结合语义指标和人工评估。

### ROUGE 与 BLEU 的一句话区别
- **一句话**：BLEU 主要问“候选文本有多精确地命中参考表达”，ROUGE 主要问“参考中的关键信息被覆盖了多少”。

---

## 2. Background & Goal

- Iteration 038 的目标是从 precision-oriented 的 BLEU 扩展到 recall-oriented 的 ROUGE，并实现 ROUGE-1 / ROUGE-2 / ROUGE-L，重点理解 coverage 在生成评测中的意义，而不是只看分数高低。  
- 在摘要任务里，核心问题通常不是“句子逐字一致”，而是“参考摘要中的关键事实有没有被保留”；因此 coverage 是更贴近任务目标的评测维度。  
- recall-oriented 指标的价值在于：它鼓励模型尽量覆盖关键事实，减少“说得通但漏要点”的输出。

---

## 3. Metric Interpretation

> 说明：当前脚本使用 `rouge_score` 的 `fmeasure`（F1 口径）作为 ROUGE-1/2/L 数值，同时 BLEU 使用 sentence-level BLEU（含平滑）。

### 3.1 BLEU
- 定位：**precision-oriented**，更关注 candidate 中有多少 n-gram 能在 reference 中命中。
- 高分意味着什么：候选表达与参考在词序/短语上较接近，字面精确度高。
- 低分意味着什么：候选与参考词面差异大，或者长度压缩/改写明显。
- 可能失效场景：
  - 语义正确但改写多（同义词、句式重组）会被低估；
  - 摘要类“压缩但保真”输出可能被惩罚过重。

### 3.2 ROUGE-1
- 定位：**unigram coverage**，衡量词级覆盖。
- 高分意味着什么：参考中的关键词/信息点较多被提到。
- 低分意味着什么：候选遗漏较多关键内容。
- 可能失效场景：
  - 只要词被提到就可能得分，无法确认结构质量；
  - 关键词堆砌可抬高分数但不一定可读。

### 3.3 ROUGE-2
- 定位：**bigram overlap**，衡量局部短语连续性与局部结构保真。
- 高分意味着什么：候选不仅提到关键词，还较好保留了相邻词关系。
- 低分意味着什么：候选发生较多改写、重排或压缩，局部连续短语难以对齐。
- 可能失效场景：
  - 对灵活改写过于苛刻，语义正确也可能低分；
  - 短文本里波动较大，稳定性受样本长度影响。

### 3.4 ROUGE-L
- 定位：基于 **Longest Common Subsequence (LCS)**，看“保序重合”。
- 高分意味着什么：候选与参考共享较长、顺序一致的词序列（可非连续匹配）。
- 低分意味着什么：即使词面重合不低，只要顺序被明显打乱，LCS 会缩短。
- 可能失效场景：
  - 语法改写/语态变换（如被动句）可能降低保序分；
  - 仍是词面重合框架，不能直接理解语义等价。

---

## 4. Experiment Design

- 数据来自 `DEMO_SAMPLES`，每个样本记录 `sample_id`、`experiment_type`、`lcs_case`、说明文本及 reference/candidate。
- 设计目标不是追求平均分，而是构造“行为可解释”的对照场景，观察各指标奖励/惩罚机制。

### experiment_type 分组与设计意图
- `exact_match`：验证上限与实现正确性（指标应接近 1.0）。
- `information_missing`：验证 coverage 缺失时 ROUGE 的响应。
- `synonym_paraphrase`：验证词面重合不足时的“语义盲区”。
- `keyword_stuffing`：检验指标是否可被投机优化。
- `long_sequence`：观察长句压缩/改写时 R1/R2/RL 的层次差异。
- `rougeL_lcs_behavior`：专门验证 LCS 对顺序保持、间隔匹配、局部重排、全局重排的响应。

---

## 5. Key Findings

### 5.1 `exact_1`（baseline correctness）
1) **观察到什么**：BLEU 与 ROUGE-1/2/L 都为 1.0。  
2) **为什么会这样**：candidate 与 reference 完全一致，词汇、短语、顺序全部对齐。  
3) **指标奖励/惩罚含义**：这是“实现与口径正确”的基线点，证明后续差异来自样本行为本身，而非工具异常。

### 5.2 `missing_1`（信息缺失）
1) **观察到什么**：BLEU 很低，但 ROUGE-1/2/L 仍保留中低分。  
2) **为什么会这样**：候选句较短，只覆盖了部分关键词与结构；精确短语命中不足拉低 BLEU。  
3) **指标奖励/惩罚含义**：ROUGE 在奖励“已覆盖的关键片段”，BLEU 更强惩罚“表达不完整/不精确”。

### 5.3 `syn_1`（同义改写）
1) **观察到什么**：语义接近，但 BLEU 与 ROUGE-2 很低（ROUGE-2 可接近 0）。  
2) **为什么会这样**：改写替换了大量词面与短语，导致 n-gram overlap 几乎消失。  
3) **指标奖励/惩罚含义**：overlap 指标主要奖励“词面重合”，对“语义等价改写”存在明显盲区（semantic blindness）。

### 5.4 `stuff_1`（keyword stuffing）
1) **观察到什么**：ROUGE-1 相对可观，但文本质量未必更好。  
2) **为什么会这样**：重复关键词提高了 unigram 覆盖，部分 overlap 被“刷高”。  
3) **指标奖励/惩罚含义**：ROUGE-1 可被投机策略利用，说明不能把高分直接等同于高质量。

### 5.5 `long_1` / `long_2`（长文本分层行为）
1) **观察到什么**：长句压缩/改写时，常见现象是 `rouge1` 相对较高，`rouge2` 更低，`rougeL` 位于中间或接近 `rouge1`。  
2) **为什么会这样**：关键词仍大量保留（利于 R1），但局部 bigram 连续性被压缩改写破坏（R2 下滑）；若主干顺序尚在，RL 仍可保持中等以上。  
3) **指标奖励/惩罚含义**：这组样本展示了“覆盖、局部连续性、全局保序”三层评价维度。

### 5.6 `lcs_1 ~ lcs_4`（ROUGE-L / LCS 核心行为）

#### `lcs_1` 顺序保持
1) 观察：各指标接近满分。  
2) 原因：词汇与顺序均对齐。  
3) 含义：作为 LCS 行为基线。

#### `lcs_2` 非连续匹配（gapped match）
1) 观察：R1 与 RL 仍高，R2 下滑。  
2) 原因：插入噪声词后，许多 unigram 仍在且总体顺序仍可对齐；但连续 bigram 被打断。  
3) 含义：RL 奖励“保序但可跳跃”的匹配机制，是它区别于 R2 的关键。

#### `lcs_3` 局部重排（local reorder）
1) 观察：R1 仍高，R2 与 RL 均下降，但通常 RL 高于 R2。  
2) 原因：词几乎都在（R1 受益），局部词对关系破坏（R2 受罚），整体主序列尚有保留（RL 仍有支撑）。  
3) 含义：RL 对局部重排有惩罚，但不像 R2 那样“几乎只看连续词对”。

#### `lcs_4` 全局重排（global reorder）
1) 观察：R1 依旧高位，R2 下降，RL 显著降低。  
2) 原因：词面覆盖高，但跨句主顺序被大幅打散，LCS 长度明显缩短。  
3) 含义：当“词都在但顺序变了”时，常见关系是 **R1 最高、RL 居中、R2 最低或共同低位**；RL 在这里提供了关键结构信号，避免只看 R1 得出“质量很好”的误判。

---

## 6. Risks & Limitations

1. **lexical overlap bias**：词面重合偏置，可能把“措辞相似”误当“质量更高”。
2. **synonym underestimation**：同义改写被低估，语义正确但分数不高。
3. **keyword stuffing exploitation**：关键词堆砌可抬高某些 overlap 分数。
4. **small demo sample limitation**：当前样本是教学型小样本，统计外推能力有限。
5. **single metric misinterpretation**：单指标解读易误判（例如只看 R1）。
6. **lack of semantic understanding**：overlap 不等于语义理解，无法评估事实一致性与推理正确性。
7. **lack of human evaluation loop**：缺少人工评审闭环时，自动分数无法覆盖可读性、有用性、真实性。

---

## 7. Conclusion

### 7.1 本轮确认的事实
- ROUGE 更适合回答“关键信息覆盖了多少”（coverage / recall-oriented）。
- BLEU 更偏精确命中（precision-oriented），在改写场景更容易偏低。
- ROUGE-L 能有效反映顺序保留，对“全局重排”有明显惩罚。

### 7.2 实践建议
- 摘要任务建议联合报告：`ROUGE-1 + ROUGE-2 + ROUGE-L`。
- BLEU 作为辅指标，用于观察字面精确匹配，而非单独决定质量。

### 7.3 可执行决策规则
- **R1 高、RL 低**：优先检查是否存在结构重排或叙事顺序失真。
- **BLEU 低、R1/RL 中等**：可能是压缩型摘要或改写型表达，需人工复核语义保真。
- **R1 高、R2 低**：说明关键词在，但短语连续性差，文本可能不够自然或结构松散。

### 7.4 下一步
- 引入语义指标（如 BERTScore）缓解同义改写低估问题。
- 加入人工评估维度（覆盖度、可读性、事实一致性）。
- 扩展更大样本与多领域实验，提升结论稳健性。
