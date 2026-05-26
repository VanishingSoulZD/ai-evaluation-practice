# Iteration 037 — 实现 BLEU，并解释它能衡量什么

## 1. 本次迭代目标

本轮正式进入：

> “自动生成质量评测”。

前面的 Day 29 ~ Day 36 主要解决：

- 数据；
- 标注；
- 一致性；
- 规范；
- 人工评测可靠性。

从本轮开始，将进入：

```text id="5kwpdp"
自动指标（Automatic Metrics）
```

的核心阶段。

本轮的重点是：

- 理解 BLEU 的原理；
- 实现 BLEU 计算；
- 观察不同生成结果对 BLEU 的影响；
- 理解 BLEU 的优点与局限。

本轮的核心不是：

> “跑出一个分数”。

而是：

> “知道这个分数到底意味着什么”。

---

# 2. 本轮在评测链路中的位置

本轮位于：

```text id="2brg9q"
生成模型输出
    ↓
参考答案（reference）
    ↓
BLEU
    ↓
自动生成质量评测
    ↓
后续 ROUGE / METEOR / BERTScore
```

BLEU 是：

> 自动文本生成评测的第一层基础指标。

它是：

- NLP 经典指标；
- 机器翻译历史核心指标；
- 后续大量生成指标的重要基础。

---

# 3. 为什么先学 BLEU

因为 BLEU 是：

> “最经典的 n-gram overlap 指标”。

很多后续指标：

- ROUGE；
- CIDEr；
- SacreBLEU；
- 部分 LLM Judge 对比思想；

都与它有关。

即使今天：

- BLEU 已经不再足够；
- 语义评测越来越重要；

但：

> 它依然是理解自动评测的起点。

---

# 4. 外部资源入口

---

## 4.1 BLEU 原始论文

BLEU 最早来自：

《BLEU: a Method for Automatic Evaluation of Machine Translation》

- [BLEU Paper (ACL Anthology)](https://aclanthology.org/P02-1040/?utm_source=chatgpt.com)

---

## 4.2 NLTK BLEU 文档

本轮推荐使用：

`nltk.translate.bleu_score`

- [NLTK BLEU Documentation](https://www.nltk.org/api/nltk.translate.bleu_score.html?utm_source=chatgpt.com)

---

## 4.3 SacreBLEU

工业界常见 BLEU 实现：

- [SacreBLEU GitHub](https://github.com/mjpost/sacrebleu?utm_source=chatgpt.com)

后续你会接触：

```text id="u2r8xr"
sacrebleu
```

它解决：

- tokenization 不统一；
- 不同实现不可比；
- benchmark 混乱；

的问题。

---

# 5. BLEU 到底衡量什么

这是本轮最重要的问题。

---

## 5.1 BLEU 衡量的是：

> n-gram 重合程度。

简单理解：

```text id="4z0bll"
模型输出
与
参考答案
有多少短语重合
```

例如：

Reference：

```text id="rmv0mv"
the cat is on the mat
```

Candidate：

```text id="gbvcrw"
the cat sat on the mat
```

BLEU 会统计：

- unigram（1-gram）；
- bigram（2-gram）；
- trigram（3-gram）；
- 4-gram；

之间的匹配情况。

---

## 5.2 BLEU 更偏向 Precision（精确率）

这是非常重要的一点。

BLEU 更关注：

> “生成内容有多少来自 reference”。

而不是：

> “reference 被覆盖了多少”。

因此：

BLEU 更偏：

```text id="j6gq3z"
precision-oriented
```

而不是 recall。

---

## 5.3 BLEU 为什么适合翻译

机器翻译的特点：

- 表达相对稳定；
- 句式变化有限；
- reference 通常比较明确。

因此：

BLEU 对：

- 翻译；
- 模板生成；
- 固定格式输出；

效果较好。

---

# 6. BLEU 的核心组成

---

## 6.1 n-gram overlap

核心思想：

```text id="oh6t6k"
短语匹配越多
BLEU 越高
```

---

## 6.2 Brevity Penalty（长度惩罚）

如果模型输出太短：

BLEU 会惩罚。

因为否则：

```text id="gpn0dj"
只输出几个高频词
也可能 precision 很高
```

所以：

BLEU 会增加：

```text id="e8c2i0"
brevity penalty
```

避免：

“极短输出骗分”。

---

## 6.3 多阶 n-gram

BLEU 不只看 unigram。

还会看：

- 2-gram；
- 3-gram；
- 4-gram。

因为：

仅 unigram 高，

不代表：

语序正确。

---

# 7. 本轮输入数据

建议继续使用：

- Day 31 抽取的生成类样本；
- QA reference answer；
- 或构造少量生成结果。

建议至少包含：

| sample_id | reference             | candidate              |
| --------- | --------------------- | ---------------------- |
| s1        | the cat is on the mat | the cat sat on the mat |

---

# 8. 本轮执行步骤

---

## Step 1：安装依赖

推荐：

```bash id="9cvn7j"
uv add nltk
```

或者：

```bash id="hmfrcl"
pip install nltk
```

---

## Step 2：实现 BLEU 计算脚本

创建：

```text id="l09c9x"
scripts/day37_bleu_eval.py
```

推荐使用：

```python id="yknj27"
from nltk.translate.bleu_score import sentence_bleu
```

---

## Step 3：准备 reference 与 candidate

BLEU 需要：

```text id="e3owb2"
reference
candidate
```

注意：

reference 可以有多个。

例如：

```python id="xgh6si"
references = [
    ["the", "cat", "is", "on", "the", "mat"]
]
```

---

## Step 4：计算 BLEU

例如：

```python id="u06e62"
score = sentence_bleu(references, candidate)
```

输出：

```text id="ut5vg5"
0 ~ 1
```

通常：

会转成：

```text id="zj4j0r"
0 ~ 100
```

百分制。

---

## Step 5：观察语序变化影响

本轮必须重点观察：

语序变化会如何影响 BLEU。

例如：

Reference：

```text id="gb9tk2"
the cat is on the mat
```

Candidate：

```text id="fslx8v"
on the mat is the cat
```

语义接近，

但 BLEU 会下降。

因为：

高阶 n-gram 被破坏。

---

## Step 6：观察同义改写影响

例如：

Reference：

```text id="cf5h4r"
the boy is happy
```

Candidate：

```text id="e4gngn"
the child feels joyful
```

语义可能正确，

但 BLEU 会很低。

这是 BLEU 最大的问题之一：

> 不理解语义。

---

# 9. BLEU 能衡量什么

---

## 9.1 能衡量字面接近程度

BLEU 擅长：

- phrase overlap；
- 固定表达；
- 模板输出。

---

## 9.2 能部分衡量语序稳定性

因为：

高阶 n-gram 会考虑：

局部语序。

---

## 9.3 对模板型任务很有效

例如：

- 翻译；
- SQL generation；
- API generation；
- 固定格式摘要。

---

# 10. BLEU 的核心局限

这是本轮最关键部分之一。

---

## 10.1 对同义改写不友好

BLEU 不理解：

```text id="o13q8x"
semantic equivalence
```

因此：

```text id="m9oz1x"
child
```

与：

```text id="j4od0y"
boy
```

不会自动认为相同。

---

## 10.2 对开放生成任务效果较差

例如：

- 对话；
- 创作；
- 长摘要；

可能存在：

大量合理表达。

但 BLEU 仍然会给低分。

---

## 10.3 高 BLEU 不代表语义一定更好

例如：

```text id="wn0g8k"
机械复读
```

可能拿到高 BLEU。

但：

并不一定：

- 信息完整；
- 逻辑正确；
- 可读性高。

---

# 11. BLEU 分数如何解读

---

## 11.1 分数很低

通常说明：

- 字面重合少；
- 改写较大；
- 偏离 reference；
- 语序变化明显。

---

## 11.2 分数中等

通常说明：

- 命中了部分关键短语；
- 有一定结构接近性。

---

## 11.3 分数较高

通常说明：

- 与 reference 表达接近；
- phrase overlap 较高。

但：

不等于：

语义一定更好。

---

# 12. 本轮建议实验

本轮强烈建议你主动构造：

---

## 12.1 完全一致样本

观察：

BLEU 接近 1。

---

## 12.2 语序变化样本

观察：

高阶 n-gram 如何下降。

---

## 12.3 同义改写样本

观察：

语义正确但 BLEU 很低。

---

## 12.4 超短输出样本

观察：

brevity penalty 如何生效。

---

# 13. 本轮脚本建议结构

建议：

```text id="5qrv6n"
scripts/day37_bleu_eval.py
```

至少包含：

- 数据读取；
- tokenization；
- BLEU 计算；
- score 输出；
- CSV 保存。

---

# 14. 本轮输出文件

---

## 14.1 BLEU 脚本

- `scripts/day37_bleu_eval.py`

---

## 14.2 BLEU 结果

- `outputs/day37_bleu_scores.csv`

建议字段：

| sample_id | bleu | reference | candidate |
| --------- | ---- | --------- | --------- |

---

## 14.3 迭代文档

- `docs/iterations/iter_037.md`

---

# 15. 验收标准

本轮结束后，需要确认：

---

## 15.1 你是否真正理解 BLEU

不是：

> “生成质量总分”。

而是：

> “n-gram overlap 指标”。

---

## 15.2 你是否理解 precision-oriented

BLEU 更关注：

```text id="gflcgh"
candidate 中有多少内容命中 reference
```

而不是：

reference 是否被完整覆盖。

---

## 15.3 你是否知道 BLEU 的局限

重点包括：

- 不理解语义；
- 不擅长开放生成；
- 对同义改写不友好。

---

# 16. 本轮执行结论

---

## 16.1 结论一：BLEU 是经典基础指标

它是：

现代自动生成评测的重要起点。

---

## 16.2 结论二：BLEU 更适合固定表达任务

例如：

- 翻译；
- 模板生成；
- 结构化输出。

---

## 16.3 结论三：BLEU 不等于“真正语义质量”

因此后面必须继续学习：

- ROUGE；
- METEOR；
- BERTScore；
- LLM Judge。

---

# 17. 下一步计划

下一轮（Day 38）将进入：

- ROUGE；
- recall-oriented 指标；
- 摘要评测；
- longest common subsequence。

---

# 18. 与本轮相关的后续文件

建议同步维护：

- `scripts/day37_bleu_eval.py`
- `outputs/day37_bleu_scores.csv`
- `docs/iterations/iter_037.md`
