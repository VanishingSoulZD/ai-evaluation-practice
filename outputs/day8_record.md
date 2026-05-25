# Day 8 练习记录：文本评测指标理解（独立版）

> 说明：本记录独立于 `docs/iterations/iter_008.md`，仅包含手工计算示例、Python 验证和总结，便于直接复习与复用。

---

## 1. 小规模示例准备

### 1.1 文本生成示例

- 参考文本（Reference, ref）：`the cat is on the mat`
- 生成文本（Candidate, cand）：`the cat sat on the mat`

分词后：

- ref = `[the, cat, is, on, the, mat]`（长度 6）
- cand = `[the, cat, sat, on, the, mat]`（长度 6）

### 1.2 分类示例

- 真实标签 `y_true`：`[1, 0, 1, 1, 0, 0, 1, 0]`
- 预测标签 `y_pred`：`[1, 1, 1, 1, 0, 0, 0, 0]`

### 1.3 对战胜率示例（模型 A vs 模型 B）

- 总样本数：10
- A 胜：6
- A 负：3
- 平局：1

---

# 2. 手工计算过程（公式 + 数值）

## 2.1 ROUGE-N（N=1,2）

### ROUGE-1（Recall 口径）

公式：

```text
ROUGE-1 =
Σ min(Count_cand(g), Count_ref(g))
-----------------------------------
Σ Count_ref(g)
```

其中 `g ∈ unigram(ref)`。

- ref unigram 计数：the×2, cat×1, is×1, on×1, mat×1
- cand unigram 计数：the×2, cat×1, sat×1, on×1, mat×1
- 重叠数（min 计数）：the×2 + cat×1 + on×1 + mat×1 = 5
- ref unigram 总数：6

```text
ROUGE-1 = 5 / 6 = 0.8333
```

---

### ROUGE-2（Recall 口径）

公式同理：

```text
ROUGE-2 =
Σ min(Count_cand(g), Count_ref(g))
-----------------------------------
Σ Count_ref(g)
```

其中 `g ∈ bigram(ref)`。

- ref bigram：`the cat`, `cat is`, `is on`, `on the`, `the mat`
- cand bigram：`the cat`, `cat sat`, `sat on`, `on the`, `the mat`
- 重叠 bigram：`the cat`, `on the`, `the mat` 共 3 个
- ref bigram 总数：5

```text
ROUGE-2 = 3 / 5 = 0.6000
```

---

## 2.2 ROUGE-L（LCS）

令最长公共子序列长度为 `LCS`：

```text
R_LCS  = LCS / |ref|
P_LCS  = LCS / |cand|
F1_LCS = 2 * R_LCS * P_LCS / (R_LCS + P_LCS)
```

- cand 与 ref 的一个 LCS：`the cat on the mat`
- LCS = 5
- `|ref| = 6`
- `|cand| = 6`

```text
R_LCS  = 5 / 6 = 0.8333
P_LCS  = 5 / 6 = 0.8333
F1_LCS = 0.8333
```

---

## 2.3 BLEU（unigram、bigram）

通式：

```text
BLEU = BP * exp( Σ w_n * log(p_n) )
```

其中：

- `p_n`：clipped n-gram precision
- `BP = min(1, e^(1-r/c))`
- `c`：候选长度
- `r`：参考长度

本例中：

```text
c = r = 6
BP = 1
```

---

### BLEU-1

- unigram clipped precision：

```text
p1 = 5 / 6 = 0.8333
```

因此：

```text
BLEU-1 = 1 × 0.8333 = 0.8333
```

---

### BLEU-2（累积到 2-gram）

- `p1 = 5 / 6 = 0.8333`
- `p2 = 3 / 5 = 0.6000`
- `w1 = w2 = 0.5`

```text
BLEU-2
= exp(0.5 * log(0.8333) + 0.5 * log(0.6000))
= sqrt(0.8333 × 0.6000)
≈ 0.7071
```

---

## 2.4 Accuracy（准确率）

公式：

```text
Accuracy = #correct / #total
```

逐项对比：

- 正确位置：1,3,4,5,6,8（共 6 个）
- 总样本：8

```text
Accuracy = 6 / 8 = 0.7500
```

---

## 2.5 Win Rate（胜率）

### 口径 A：不计平局

```text
WinRate = W / (W + L)
         = 6 / (6 + 3)
         = 0.6667
```

---

### 口径 B：平局折半

```text
WinRate_tie0.5
= (W + 0.5 * T) / (W + L + T)
= (6 + 0.5 × 1) / 10
= 0.6500
```

---

## 3. Python 验证（与手工结果一致）

```bash
uv run python -m scripts.day8_record
```

---

## 4. 指标总结：含义、适用场景、局限性

### ROUGE

- 含义：衡量生成文本对参考文本关键信息的覆盖程度（常用 Recall 口径）。
- 适用场景：摘要、改写、问答生成（有参考答案时）。

局限性：

- 依赖词面重叠，难评估语义等价改写；
- 对分词/预处理敏感；
- 单参考答案时容易低估多样正确表达。

---

### BLEU

- 含义：衡量候选文本与参考文本的 n-gram 精确匹配程度，并通过 BP 惩罚过短句。
- 适用场景：机器翻译、受约束文本生成。

局限性：

- 词面不同但语义正确时分数可能偏低；
- 句级 BLEU 在小样本上波动较大（常需平滑）；
- 不能直接衡量事实正确性与可读性。

---

### Accuracy

- 含义：预测正确样本占比。
- 适用场景：类别较均衡且错误代价相近的分类任务。

局限性：

- 类别不平衡下可能误导；
- 不能体现不同类型错误代价差异，应配合 Precision / Recall / F1。

---

### Win Rate

- 含义：在对比评测中，一个系统“赢”另一个系统的比例。
- 适用场景：A/B 测试、人类偏好评测、模型对战。

局限性：

- 受评审标准和样本分布影响大；
- 平局处理方式会影响结论；
- 属于相对指标，不是绝对质量分。

---

## 5. 可复用结论提示

1. 对比结果前先统一指标口径（如 ROUGE 的 recall/F1、Win Rate 平局规则）。
2. 文本生成任务建议“自动指标 + 人工评审”联合评估，避免单一指标偏差。
3. 分类任务中 Accuracy 不够时，应至少补充 F1 或混淆矩阵。
4. 评测时固定 tokenization、大小写与标点规则，保证可复现。
5. 小样本验证优先做手工推导，再用脚本回归检查，能更快定位理解错误。
