# Iteration 040 — 实现 BERTScore，并理解语义级评测

## 1. 本次迭代目标

本轮正式进入：

> “语义级（semantic-level）文本生成评测”。

前几轮已经完成：

- BLEU；
- ROUGE；
- METEOR；
- overlap-based evaluation；
- lexical matching；
- recall / precision；
- 词级匹配。

但这些传统指标有一个根本问题：

```text id="a7k2lp"
它们主要依赖“字面相似”
```

即使：

- 语义正确；
- 表达自然；
- 改写优秀；

如果：

```text id="q9m3xc"
词面 overlap 不高
```

仍然可能低分。

因此：

本轮将正式进入：

```text id="r4y8nv"
embedding-based semantic evaluation
```

也就是：

```text id="n5u1hj"
BERTScore
```

---

# 2. 本轮在评测链路中的位置

本轮位于：

```text id="m8v2pa"
BLEU / ROUGE / METEOR
    ↓
BERTScore
    ↓
semantic similarity
    ↓
后续 LLM-as-a-Judge
```

BERTScore 是：

- embedding-based metric；
- contextual semantic evaluation；
- 现代 generation evaluation 的关键里程碑。

它代表：

```text id="f2q7od"
评测开始从“字面匹配”
进入
“语义相似”
```

---

# 3. 为什么需要 BERTScore

传统指标的问题：

---

## BLEU

太依赖：

```text id="w7c4ye"
exact n-gram overlap
```

---

## ROUGE

更关注：

```text id="j3z9lf"
coverage
```

但：

仍然不理解语义。

---

## METEOR

虽然更灵活。

但本质上：

仍然主要依赖：

```text id="h4p8rm"
lexical matching
```

---

因此：

需要一种指标：

即使：

- 用词不同；
- 句式不同；
- 同义改写很多；

也能认为：

```text id="c6x1sz"
“它们语义接近”
```

这就是：

```text id="u9n5tb"
BERTScore
```

的核心目标。

---

# 4. 外部资源入口

---

## 4.1 BERTScore 原始论文

BERTScore 最早来自：

《BERTScore: Evaluating Text Generation with BERT》

- [BERTScore Paper (ICLR/OpenReview)](https://openreview.net/forum?id=SkeHuCVFDr&utm_source=chatgpt.com)

---

## 4.2 官方 GitHub

- [BERTScore GitHub](https://github.com/Tiiiger/bert_score?utm_source=chatgpt.com)

---

## 4.3 Hugging Face Evaluate

后续也可统一使用：

- [Hugging Face Evaluate Documentation](https://huggingface.co/docs/evaluate/index?utm_source=chatgpt.com)

---

# 5. BERTScore 到底是什么

这是本轮最重要的问题。

---

## 5.1 BERTScore 不再比较“词是否一样”

而是比较：

```text id="j6y0nc"
词在上下文中的 embedding 是否接近
```

例如：

Reference：

```text id="g5w2lr"
the boy is happy
```

Candidate：

```text id="s3u7mx"
the child feels joyful
```

BLEU：

可能很低。

但：

BERTScore 会发现：

```text id="r7k4pd"
boy ↔ child
happy ↔ joyful
```

在 embedding space 中：

非常接近。

因此：

BERTScore 往往更高。

---

# 6. 什么是 Contextual Embedding

这是本轮必须真正理解的核心。

传统词向量时代：

```text id="n1h5yb"
bank
```

只有一个固定向量。

但：

BERT 类模型会根据上下文生成：

```text id="k8v3oj"
contextual embedding
```

例如：

---

### 金融语境

```text id="x4t6ca"
I deposited money in the bank.
```

---

### 河岸语境

```text id="u2m9ze"
He sat on the river bank.
```

这里：

```text id="d5r1qw"
bank
```

的 embedding 会不同。

因此：

BERTScore 比传统 lexical overlap：

更接近语义理解。

---

# 7. BERTScore 的核心思想

---

## Step 1：编码 reference 与 candidate

使用：

- BERT；
- RoBERTa；
- DeBERTa；
- 等 Transformer encoder。

得到：

```text id="p7x4vf"
token embeddings
```

---

## Step 2：逐 token 匹配

BERTScore 会计算：

```text id="n6z8kh"
candidate token
与
reference token
之间的 cosine similarity
```

---

## Step 3：计算 Precision / Recall / F1

最终输出：

- Precision；
- Recall；
- F1。

通常：

最常使用：

```text id="q3w9jt"
F1
```

---

# 8. 为什么 BERTScore 更接近人工判断

因为人工判断时：

人会认为：

```text id="l0f8ya"
同义改写
≈
语义一致
```

而不是：

必须逐词一致。

BERTScore 更接近：

这种认知。

---

# 9. 本轮输入数据

本轮必须重点构造：

```text id="m2r5pb"
“字面差异大但语义接近”
```

的样本。

建议包含：

| sample_id | reference        | candidate                  |
| --------- | ---------------- | -------------------------- |
| s1        | the boy is happy | the child feels joyful     |
| s2        | he bought a car  | he purchased an automobile |

---

# 10. 本轮执行步骤

---

## Step 1：安装依赖

推荐：

```bash id="z8v1pw"
uv add bert-score torch transformers
```

或者：

```bash id="y7k4ex"
pip install bert-score torch transformers
```

---

# 10.2 创建脚本

创建：

```text id="a9f6qm"
scripts/day40_bertscore_eval.py
```

---

# 10.3 导入 BERTScore

推荐：

```python id="x3v8lw"
from bert_score import score
```

---

# 10.4 计算 BERTScore

例如：

```python id="r5p2od"
P, R, F1 = score(
    candidates,
    references,
    lang="en"
)
```

输出：

- Precision；
- Recall；
- F1 tensor。

---

# 10.5 保存结果

建议保存：

- bertscore_precision；
- bertscore_recall；
- bertscore_f1。

---

# 11. 本轮必须重点观察的现象

这是本轮最关键部分。

---

# 11.1 同义改写

例如：

Reference：

```text id="k2x9ra"
the boy is happy
```

Candidate：

```text id="t6v3ec"
the child feels joyful
```

通常：

| 指标      | 结果 |
| --------- | ---- |
| BLEU      | 低   |
| ROUGE     | 中等 |
| METEOR    | 较高 |
| BERTScore | 很高 |

---

# 11.2 句式改写

例如：

Reference：

```text id="w1p4mb"
she completed the work quickly
```

Candidate：

```text id="n8r6yv"
the task was finished rapidly by her
```

BERTScore 往往：

明显高于 BLEU。

---

# 11.3 语义错误但 overlap 高

这是非常重要的情况。

例如：

Reference：

```text id="c4x8zu"
the patient survived the surgery
```

Candidate：

```text id="m5t1lf"
the patient died after the surgery
```

某些 overlap 指标：

可能不低。

但：

语义已经相反。

BERTScore：

有时会下降，

但：

```text id="v9k3ra"
仍然不一定足够可靠
```

这是本轮必须真正理解的重点。

---

# 12. BERTScore 能衡量什么

---

# 12.1 语义相似

这是核心能力。

尤其适合：

- paraphrase；
- QA generation；
- 摘要；
- 开放文本生成。

---

# 12.2 同义改写

BERTScore 对：

- synonym；
- wording variation；

明显更友好。

---

# 12.3 上下文语义

由于使用 contextual embeddings：

因此：

它比传统 lexical metrics：

更接近真实语言理解。

---

# 13. BERTScore 的核心局限

这是本轮必须真正理解的部分。

---

# 13.1 语义接近 ≠ 事实正确

例如：

Reference：

```text id="b7r2xc"
Paris is the capital of France.
```

Candidate：

```text id="e3v5qt"
Lyon is the capital of France.
```

embedding 可能仍然：

有一定相似性。

因此：

BERTScore：

```text id="h8m1zw"
不是 factuality metric
```

---

# 13.2 高语义相似不等于逻辑正确

它不真正做：

- reasoning；
- verification；
- world modeling。

---

# 13.3 对 hallucination 不一定稳定

例如：

生成：

- 多余事实；
- 编造细节；

BERTScore 可能仍不低。

---

# 13.4 计算成本明显更高

相比：

- BLEU；
- ROUGE；
- METEOR；

BERTScore：

需要：

- Transformer inference；
- embedding 计算；
- GPU/CPU 更多资源。

---

# 14. BLEU / ROUGE / METEOR / BERTScore 对比

这是本轮必须建立的核心认知。

| 指标      | 核心思想               | 更关注       |
| --------- | ---------------------- | ------------ |
| BLEU      | n-gram precision       | 字面精确匹配 |
| ROUGE     | coverage / recall      | 信息覆盖     |
| METEOR    | flexible lexical match | 灵活词级匹配 |
| BERTScore | embedding similarity   | 语义相似     |

---

# 15. 本轮建议实验

强烈建议主动构造：

---

# 15.1 同义改写样本

观察：

BERTScore 如何明显高于 BLEU。

---

# 15.2 句式改写样本

观察：

semantic similarity 的优势。

---

# 15.3 事实错误样本

观察：

BERTScore 的局限。

---

# 15.4 hallucination 样本

观察：

embedding similarity 不一定可靠。

---

# 16. 本轮脚本建议结构

建议：

```text id="q6v8re"
scripts/day40_bertscore_eval.py
```

至少包含：

- 数据读取；
- bert-score；
- precision；
- recall；
- f1；
- CSV 输出；
- 与 BLEU / ROUGE / METEOR 对比。

---

# 17. 本轮输出文件

---

## 17.1 BERTScore 脚本

- `scripts/day40_bertscore_eval.py`

---

## 17.2 BERTScore 结果

- `outputs/day40_bertscore_scores.csv`

建议字段：

| sample_id | bertscore_p | bertscore_r | bertscore_f1 | bleu | rougeL | meteor |
| --------- | ----------- | ----------- | ------------ | ---- | ------ | ------ |

---

## 17.3 迭代文档

- `docs/iterations/iter_040.md`

---

# 18. 验收标准

本轮结束后，需要确认：

---

# 18.1 你是否真正理解 semantic evaluation

不是：

```text id="z4t7ko"
“字面是否一样”
```

而是：

```text id="j8v3pr"
“语义是否接近”
```

---

# 18.2 你是否理解 contextual embeddings

包括：

- 上下文相关；
- token embedding；
- semantic similarity。

---

# 18.3 你是否知道 BERTScore 的局限

包括：

- 不保证 factual correctness；
- 不保证 reasoning；
- 不一定能识别 hallucination。

---

# 19. 本轮执行结论

---

# 19.1 结论一：BERTScore 是语义级评测的重要转折点

它代表：

```text id="u3p9xf"
generation evaluation
从 lexical overlap
进入 semantic similarity
```

---

# 19.2 结论二：它比传统指标更接近人工判断

尤其在：

- paraphrase；
- 开放生成；
- 灵活表达；

中更明显。

---

# 19.3 结论三：语义相似仍然不等于真实正确

因此：

后续必须继续进入：

- factuality；
- hallucination；
- LLM Judge；
- pairwise evaluation；
- MT-Bench。

---

# 20. 下一步计划

下一轮（Day 41）将进入：

- OpenCompass；
- MT-Bench；
- LLM-as-a-Judge；
- 现代 LLM 评测体系。

---

# 21. 与本轮相关的后续文件

建议同步维护：

- `scripts/day40_bertscore_eval.py`
- `outputs/day40_bertscore_scores.csv`
- `docs/iterations/iter_040.md`
