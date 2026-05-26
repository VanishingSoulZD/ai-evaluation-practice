# Iteration 038 — 实现 ROUGE，并解释它能衡量什么

## 1. 本次迭代目标

本轮正式进入：

> “覆盖型（Recall-Oriented）自动评测指标”。

上一轮（Day 37）已经完成：

- BLEU；
- precision-oriented 指标；
- n-gram overlap；
- 翻译类评测逻辑。

本轮则进入：

```text id="p0y1xk"
ROUGE（Recall-Oriented Understudy for Gisting Evaluation）
```

的核心阶段。

本轮的重点是：

- 理解 ROUGE 的原理；
- 实现 ROUGE-1 / ROUGE-2 / ROUGE-L；
- 理解 recall-oriented 指标；
- 对比 BLEU 与 ROUGE 的差异；
- 理解为什么摘要任务更偏向 ROUGE。

本轮最重要的事情不是：

> “跑出 ROUGE 分数”。

而是：

> “理解覆盖（coverage）在生成评测中的意义”。

---

# 2. 本轮在评测链路中的位置

本轮位于：

```text id="x2t8aw"
生成模型输出
    ↓
参考答案（reference）
    ↓
ROUGE
    ↓
摘要 / 长文本评测
    ↓
后续 METEOR / BERTScore
```

ROUGE 是：

- 摘要评测经典指标；
- 长文本生成核心基础指标；
- QA generation 常用指标；
- 后续许多 summarization benchmark 的基础。

---

# 3. 为什么要学习 ROUGE

BLEU 更偏：

```text id="9cll7o"
precision-oriented
```

它更关注：

> candidate 有多少内容命中了 reference。

但：

摘要任务真正关心的是：

> “reference 中的重要信息是否被覆盖”。

因此：

ROUGE 更强调：

```text id="uyg0s6"
coverage
```

也就是：

```text id="q2g9wf"
recall-oriented
```

---

# 4. 外部资源入口

---

## 4.1 ROUGE 原始论文

ROUGE 最早来自：

《ROUGE: A Package for Automatic Evaluation of Summaries》

- [ROUGE Paper (ACL Anthology)](https://aclanthology.org/W04-1013/?utm_source=chatgpt.com)

---

## 4.2 rouge-score 官方实现

Google 的 rouge-score：

- [Google rouge-score GitHub](https://github.com/google-research/google-research/tree/master/rouge?utm_source=chatgpt.com)

---

## 4.3 Hugging Face Evaluate

后续你会大量接触：

- [Hugging Face Evaluate](https://huggingface.co/docs/evaluate/index?utm_source=chatgpt.com)

其中包含：

- BLEU；
- ROUGE；
- BERTScore；
- SacreBLEU；
- Accuracy；
- F1；

等统一评测接口。

---

# 5. ROUGE 到底衡量什么

这是本轮最重要的问题。

---

## 5.1 ROUGE 更关注“参考内容是否被覆盖”

简单理解：

```text id="ihxj7u"
reference 中的重要内容
是否出现在 candidate 中
```

例如：

Reference：

```text id="t3w3cx"
The cat sat on the mat and looked outside.
```

Candidate：

```text id="7rkl0q"
The cat sat on the mat.
```

BLEU 可能不低。

但：

ROUGE 会注意到：

```text id="k14h8y"
looked outside
```

没有被覆盖。

---

## 5.2 为什么摘要任务更适合 ROUGE

摘要任务核心是：

> 保留关键信息。

因此：

更重要的是：

```text id="q4z6mv"
信息覆盖率
```

而不是：

```text id="k6v1ev"
表达是否完全一致
```

---

# 6. ROUGE 的核心组成

---

# 6.1 ROUGE-1

衡量：

```text id="rq8f7x"
unigram overlap
```

即：

单词级覆盖。

例如：

Reference：

```text id="k3lfuy"
the cat sat on the mat
```

Candidate：

```text id="z0ec5z"
the cat is on mat
```

ROUGE-1 会统计：

有多少词被覆盖。

---

# 6.2 ROUGE-2

衡量：

```text id="hnl3m2"
bigram overlap
```

即：

短语级覆盖。

它比 ROUGE-1 更严格。

因为：

不仅要求词出现，

还要求局部顺序接近。

---

# 6.3 ROUGE-L

这是本轮非常重要的部分。

ROUGE-L 基于：

```text id="tf1f9x"
Longest Common Subsequence（LCS）
```

即：

最长公共子序列。

它不要求连续，

但要求：

```text id="jzjw2g"
相对顺序保持
```

---

# 7. 为什么 ROUGE-L 很重要

ROUGE-L 更接近：

> “整体序列结构”。

例如：

Reference：

```text id="pcdf93"
A B C D E
```

Candidate：

```text id="sfv1cm"
A X B Y C D
```

最长公共子序列：

```text id="8yjlwm"
A B C D
```

因此：

ROUGE-L 能部分衡量：

- 序列结构；
- 内容组织；
- 长文本覆盖。

---

# 8. 本轮输入数据

建议继续使用：

- Day 31 的生成任务样本；
- QA generation；
- 摘要样本；
- reference / candidate 对。

建议至少包含：

| sample_id | reference              | candidate             |
| --------- | ---------------------- | --------------------- |
| s1        | the cat sat on the mat | the cat is on the mat |

---

# 9. 本轮执行步骤

---

## Step 1：安装依赖

推荐：

```bash id="w6l5cw"
uv add rouge-score
```

或者：

```bash id="v3h7od"
pip install rouge-score
```

---

## Step 2：实现 ROUGE 脚本

创建：

```text id="4e8jlwm"
scripts/day38_rouge_eval.py
```

推荐使用：

```python id="2e2k4n"
from rouge_score import rouge_scorer
```

---

## Step 3：初始化 scorer

例如：

```python id="4icj8k"
scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],
    use_stemmer=True
)
```

---

## Step 4：计算 ROUGE

例如：

```python id="dbyyru"
scores = scorer.score(reference, candidate)
```

输出：

- rouge1；
- rouge2；
- rougeL。

通常包含：

- precision；
- recall；
- fmeasure。

---

## Step 5：与 BLEU 对照

这是本轮最关键部分之一。

同一批样本：

同时计算：

- BLEU；
- ROUGE。

重点观察：

- 哪些样本 BLEU 低但 ROUGE 高；
- 哪些样本 ROUGE 高但人工体验差；
- 哪些样本存在冗余堆砌。

---

# 10. BLEU 与 ROUGE 的核心差异

---

## 10.1 BLEU 更偏 Precision

BLEU 关注：

```text id="7zqlrk"
candidate 中有多少内容命中 reference
```

---

## 10.2 ROUGE 更偏 Recall

ROUGE 关注：

```text id="vz7jrl"
reference 中有多少内容被覆盖
```

---

## 10.3 为什么摘要更偏 ROUGE

摘要最重要的是：

```text id="mjlwm4"
不要遗漏关键信息
```

因此：

coverage 更重要。

---

# 11. ROUGE 能衡量什么

---

## 11.1 信息覆盖

ROUGE 很适合：

- 摘要；
- QA generation；
- 长文本概括；
- 信息提取型生成。

---

## 11.2 部分序列结构

尤其是：

```text id="pbqjzv"
ROUGE-L
```

可以衡量：

- 长序列结构；
- 内容顺序；
- 句子组织。

---

## 11.3 长文本 recall

在长文本中：

ROUGE 更能反映：

```text id="0n1pl9"
reference 是否被“讲到”
```

---

# 12. ROUGE 的核心局限

这是本轮必须真正理解的部分。

---

## 12.1 ROUGE 不理解语义

例如：

Reference：

```text id="9o74kr"
the boy is happy
```

Candidate：

```text id="z7a6r5"
the child feels joyful
```

ROUGE 可能仍然不高。

因为：

词面 overlap 较少。

---

## 12.2 高 ROUGE 不代表自然

例如：

```text id="14a9gn"
关键词堆砌
```

可能拿到高 ROUGE。

但：

人工阅读体验很差。

---

## 12.3 ROUGE 容易被冗余骗分

例如：

```text id="k8m7lf"
重复 reference 内容
```

可能提高 recall。

但：

并不代表：

摘要质量更高。

---

# 13. ROUGE 分数如何解读

---

## 13.1 ROUGE 低

通常说明：

- 关键内容未覆盖；
- 信息遗漏；
- 偏离 reference。

---

## 13.2 ROUGE 中等

通常说明：

- 覆盖部分关键信息；
- 存在缺失。

---

## 13.3 ROUGE 较高

通常说明：

- 主要信息点被包含；
- 内容覆盖较完整。

但：

不代表：

- 表达自然；
- 逻辑优秀；
- 摘要简洁。

---

# 14. 本轮建议实验

本轮强烈建议主动构造：

---

## 14.1 信息遗漏样本

观察：

ROUGE recall 如何下降。

---

## 14.2 关键词堆砌样本

观察：

ROUGE 可能仍然偏高。

---

## 14.3 同义改写样本

观察：

语义正确但 overlap 不高。

---

## 14.4 长文本摘要样本

观察：

ROUGE-L 的效果。

---

# 15. 本轮脚本建议结构

建议：

```text id="z1d7ru"
scripts/day38_rouge_eval.py
```

至少包含：

- 数据读取；
- ROUGE scorer；
- rouge1；
- rouge2；
- rougeL；
- CSV 输出。

---

# 16. 本轮输出文件

---

## 16.1 ROUGE 脚本

- `scripts/day38_rouge_eval.py`

---

## 16.2 ROUGE 结果

- `outputs/day38_rouge_scores.csv`

建议字段：

| sample_id | rouge1 | rouge2 | rougeL | reference | candidate |
| --------- | ------ | ------ | ------ | --------- | --------- |

---

## 16.3 迭代文档

- `docs/iterations/iter_038.md`

---

# 17. 验收标准

本轮结束后，需要确认：

---

## 17.1 你是否真正理解 ROUGE

不是：

> “另一个 overlap 分数”。

而是：

> “coverage-oriented 指标”。

---

## 17.2 你是否理解 recall-oriented

ROUGE 更关注：

```text id="7og4yl"
reference 是否被覆盖
```

而不是：

candidate 是否“精确”。

---

## 17.3 你是否知道 ROUGE 的局限

包括：

- 不理解语义；
- 可被冗余骗分；
- 高 ROUGE 不等于高质量。

---

# 18. 本轮执行结论

---

## 18.1 结论一：ROUGE 是摘要评测核心指标

尤其适用于：

- summarization；
- QA generation；
- 长文本生成。

---

## 18.2 结论二：ROUGE 与 BLEU 关注点不同

BLEU：

```text id="7s8m7g"
precision
```

ROUGE：

```text id="mkjlwm"
recall
```

---

## 18.3 结论三：ROUGE 仍然不是真正语义评测

因此后续必须继续进入：

- METEOR；
- BERTScore；
- embedding-based metrics；
- LLM Judge。

---

# 19. 下一步计划

下一轮（Day 39）将进入：

- METEOR；
- 同义词；
- stemming；
- 语义匹配增强。

---

# 20. 与本轮相关的后续文件

建议同步维护：

- `scripts/day38_rouge_eval.py`
- `outputs/day38_rouge_scores.csv`
- `docs/iterations/iter_038.md`
