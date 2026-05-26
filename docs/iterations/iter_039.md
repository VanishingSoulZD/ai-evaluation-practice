# Iteration 039 — 实现 METEOR，并理解它和前两个指标的差异

## 1. 本次迭代目标

本轮正式进入：

> “更接近人工判断的传统生成评测指标”。

前两轮已经完成：

- BLEU；
- ROUGE；
- precision-oriented；
- recall-oriented；
- n-gram overlap；
- coverage。

但这两个指标有一个共同问题：

```text id="b2lz8n"
它们过于依赖字面重合（surface overlap）
```

因此：

- 同义改写；
- 词形变化；
- 灵活表达；

往往会被低估。

本轮的目标就是理解：

```text id="vqlr8f"
METEOR 为什么比 BLEU / ROUGE 更“宽松”
```

以及：

> 为什么它通常与人工判断更接近。

---

# 2. 本轮在评测链路中的位置

本轮位于：

```text id="v7a9lh"
BLEU / ROUGE
    ↓
METEOR
    ↓
更灵活的传统文本匹配
    ↓
后续 embedding-based metrics
```

METEOR 是：

- BLEU 的重要改进方向；
- 传统 generation evaluation 的关键指标；
- 后续 semantic metrics 的过渡层。

---

# 3. 为什么还需要 METEOR

BLEU 的问题：

- 太依赖精确短语匹配；
- 对同义改写不友好；
- 对词形变化不友好。

ROUGE 的问题：

- 依然主要依赖 overlap；
- 更关注 coverage；
- 仍然不理解语义。

因此：

METEOR 试图解决：

```text id="wl1qv7"
“表达不同但语义接近”
```

的问题。

---

# 4. 外部资源入口

---

## 4.1 METEOR 原始论文

METEOR 最早来自：

《METEOR: An Automatic Metric for MT Evaluation with Improved Correlation with Human Judgments》

- [METEOR Paper (ACL Anthology)](https://aclanthology.org/W05-0909/?utm_source=chatgpt.com)

---

## 4.2 NLTK METEOR 文档

本轮推荐使用：

`nltk.translate.meteor_score`

- [NLTK METEOR Documentation](https://www.nltk.org/api/nltk.translate.meteor_score.html?utm_source=chatgpt.com)

---

## 4.3 NLTK 官网

- [NLTK Official Site](https://www.nltk.org/?utm_source=chatgpt.com)

---

# 5. METEOR 到底衡量什么

这是本轮最重要的问题。

---

## 5.1 METEOR 更关注“灵活匹配”

METEOR 不只是看：

```text id="bt1m5y"
exact n-gram overlap
```

它还会考虑：

- stemming；
- synonym matching；
- flexible alignment；
- recall + precision 平衡。

因此：

它更接近：

```text id="krj5ey"
human judgment
```

---

## 5.2 为什么它比 BLEU 更宽松

例如：

Reference：

```text id="0n4f0v"
the boy is happy
```

Candidate：

```text id="nyjlwm"
the child feels joyful
```

BLEU：

可能很低。

ROUGE：

可能也不高。

但：

METEOR 更容易认为：

```text id="jlwm4m"
这两句“接近”
```

因为：

它允许：

- 词形变化；
- 同义词；
- 更灵活匹配。

---

# 6. METEOR 的核心组成

---

# 6.1 Exact Match

首先：

仍然会计算：

```text id="2mjlwm"
exact token match
```

---

# 6.2 Stem Match

METEOR 会考虑：

```text id="jlwm8s"
stemming
```

例如：

```text id="jlwm9z"
run
running
runs
```

会被认为：

部分相关。

---

# 6.3 Synonym Match

METEOR 还能利用：

```text id="jlwm0k"
WordNet synonym
```

例如：

```text id="jlwm7r"
boy ↔ child
happy ↔ joyful
```

因此：

它比 BLEU 更接近：

语义匹配。

---

# 6.4 Precision + Recall 平衡

BLEU 更偏 precision。

ROUGE 更偏 recall。

METEOR 会综合：

- precision；
- recall；

并进行平衡。

因此：

它通常更稳定。

---

# 7. 为什么 METEOR 更接近人工判断

因为人工评测时：

人不会只看：

```text id="jlwm5c"
字面是否完全一致
```

而会看：

- 语义；
- 改写；
- 信息是否保留；
- 表达是否合理。

METEOR 在传统指标里：

已经开始接近这种思想。

---

# 8. 本轮输入数据

建议继续使用：

- Day 31 的生成样本；
- QA generation；
- 摘要样本；
- BLEU / ROUGE 同批数据。

建议字段：

| sample_id | reference        | candidate              |
| --------- | ---------------- | ---------------------- |
| s1        | the boy is happy | the child feels joyful |

---

# 9. 本轮执行步骤

---

## Step 1：安装依赖

推荐：

```bash id="jlwm8p"
uv add nltk
```

或者：

```bash id="jlwm2n"
pip install nltk
```

---

## Step 2：下载 WordNet 资源

METEOR 常需要：

```python id="jlwm6d"
nltk.download("wordnet")
```

以及：

```python id="jlwm3h"
nltk.download("omw-1.4")
```

因为：

同义词匹配依赖 WordNet。

---

## Step 3：创建脚本

创建：

```text id="jlwm1j"
scripts/day39_meteor_eval.py
```

---

## Step 4：实现 METEOR

推荐使用：

```python id="jlwm7x"
from nltk.translate.meteor_score import meteor_score
```

例如：

```python id="jlwm4f"
score = meteor_score(
    [reference_tokens],
    candidate_tokens
)
```

---

## Step 5：与 BLEU / ROUGE 对比

这是本轮最重要部分之一。

重点观察：

---

### 情况一：同义改写

通常：

- BLEU 低；
- ROUGE 中等；
- METEOR 更高。

---

### 情况二：词形变化

例如：

```text id="jlwm2q"
run
running
runs
```

METEOR 更容易识别。

---

### 情况三：语义接近但 phrasing 不同

METEOR 往往比 BLEU 更稳定。

---

# 10. METEOR 能衡量什么

---

## 10.1 灵活表达

适合：

- paraphrase；
- QA generation；
- 更自由文本生成。

---

## 10.2 词形变化

相比 BLEU：

更不容易：

因为 morphology 被严重惩罚。

---

## 10.3 更接近人工偏好

尤其在：

- 小规模生成任务；
- 开放表达；
- QA；

中更明显。

---

# 11. METEOR 的局限

这是本轮必须真正理解的部分。

---

## 11.1 仍然不是深层语义理解

METEOR 虽然更灵活。

但：

仍然属于：

```text id="jlwm3b"
surface-level metric
```

它仍然：

不真正理解：

- factuality；
- 推理；
- 逻辑；
- 世界知识。

---

## 11.2 同义词覆盖有限

它依赖：

```text id="jlwm8v"
WordNet
```

因此：

覆盖并不完整。

很多现代表达：

- slang；
- domain terminology；
- 新词；

不一定有效。

---

## 11.3 长文本效果有限

对于：

- 长摘要；
- 长对话；
- reasoning；

METEOR 仍然不足。

---

# 12. BLEU / ROUGE / METEOR 对比（本轮重点）

这是本轮必须形成的核心认知。

---

# 12.1 BLEU

更偏：

```text id="jlwm9m"
precision
```

适合：

- 翻译；
- 模板生成；
- 固定表达。

问题：

- 太严格；
- 不理解改写。

---

# 12.2 ROUGE

更偏：

```text id="jlwm5t"
coverage / recall
```

适合：

- 摘要；
- 长文本；
- QA coverage。

问题：

- 容易被冗余骗分；
- 不理解语义。

---

# 12.3 METEOR

更偏：

```text id="jlwm0p"
flexible lexical matching
```

适合：

- 表达不完全固定；
- paraphrase；
- QA generation。

问题：

- 仍然不是 semantic evaluation。

---

# 13. 本轮建议实验

强烈建议主动构造：

---

## 13.1 同义改写样本

观察：

METEOR 为什么明显高于 BLEU。

---

## 13.2 词形变化样本

观察：

stemming 如何影响分数。

---

## 13.3 长文本样本

观察：

METEOR 的局限。

---

## 13.4 冗余样本

观察：

METEOR 是否比 ROUGE 更稳定。

---

# 14. 本轮脚本建议结构

建议：

```text id="jlwm4w"
scripts/day39_meteor_eval.py
```

至少包含：

- 数据读取；
- tokenization；
- METEOR；
- CSV 输出；
- BLEU / ROUGE 对比列。

---

# 15. 本轮输出文件

---

## 15.1 METEOR 脚本

- `scripts/day39_meteor_eval.py`

---

## 15.2 METEOR 结果

- `outputs/day39_meteor_scores.csv`

建议字段：

| sample_id | meteor | bleu | rougeL | reference | candidate |
| --------- | ------ | ---- | ------ | --------- | --------- |

---

## 15.3 迭代文档

- `docs/iterations/iter_039.md`

---

# 16. 验收标准

本轮结束后，需要确认：

---

## 16.1 你是否真正理解 METEOR

不是：

> “另一个 overlap 指标”。

而是：

> “更灵活、更接近人工判断的传统指标”。

---

## 16.2 你是否理解它为什么比 BLEU 更宽松

包括：

- stemming；
- synonym match；
- recall + precision 平衡。

---

## 16.3 你是否知道它仍然有限

包括：

- 不真正理解语义；
- 不理解事实；
- 不理解推理。

---

# 17. 本轮执行结论

---

## 17.1 结论一：METEOR 是传统指标的重要改进

它比：

- BLEU；
- ROUGE；

更接近：

人工感知。

---

## 17.2 结论二：METEOR 更适合灵活表达任务

尤其：

- paraphrase；
- QA generation；
- 较自由文本生成。

---

## 17.3 结论三：传统指标仍然不够

因此后面必须继续进入：

- embedding-based metrics；
- BERTScore；
- semantic similarity；
- LLM Judge。

---

# 18. 下一步计划

下一轮（Day 40）将进入：

- BERTScore；
- embedding similarity；
- semantic evaluation；
- contextual embeddings。

---

# 19. 与本轮相关的后续文件

建议同步维护：

- `scripts/day39_meteor_eval.py`
- `outputs/day39_meteor_scores.csv`
- `docs/iterations/iter_039.md`
