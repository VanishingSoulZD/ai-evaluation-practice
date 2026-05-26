# Iteration 036 — 计算 Cohen’s Kappa 并解释结果

## 1. 本次迭代目标

本轮的目标是正式进入：

> “标注一致性的量化阶段”。

上一轮（Day 35）已经完成：

- 双人标注；
- disagreement analysis；
- 分歧分类；
- 规范返工分析。

本轮则要把：

> “感觉一致 / 不一致”

变成：

> “可量化的一致性指标”。

核心任务是：

- 计算 Cohen’s Kappa；
- 理解 Kappa 的数学含义；
- 按标签与子任务分析稳定性；
- 判断问题到底来自：
  - 标注规范；
  - 标签设计；
  - 样本本身；
  - 还是标注者。

---

# 2. 本轮在评测链路中的位置

本轮位于：

```text
双人标注
    ↓
分歧分析
    ↓
Cohen's Kappa
    ↓
规范修订
    ↓
稳定标注数据
    ↓
自动指标 / judge
```

这一层的作用是：

> 判断“数据是否可信”。

如果这一层不稳定：

后面的：

- 自动指标；
- LLM Judge；
- Benchmark；

都会失真。

---

# 3. 外部资源入口

---

## 3.1 Cohen’s Kappa 介绍

- [Wikipedia - Cohen's Kappa](https://en.wikipedia.org/wiki/Cohen%27s_kappa?utm_source=chatgpt.com)

---

## 3.2 sklearn 官方文档

本轮推荐使用：

`sklearn.metrics.cohen_kappa_score`

- [scikit-learn Cohen Kappa Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html?utm_source=chatgpt.com)

---

## 3.3 scikit-learn 官网

- [scikit-learn](https://scikit-learn.org/stable/?utm_source=chatgpt.com)

---

# 4. 本轮为什么必须学习 Kappa

很多人会误以为：

> “一致率高”就代表标注质量高。

这是错误的。

因为：

即使随机乱标，

在类别分布极不平衡时，

也可能出现很高的一致率。

例如：

```text
95% 样本都是 positive
两个人全都只标 positive
一致率依然可能很高
```

但这并不代表：

- 标注规范清晰；
- 标注质量高；
- 标签体系稳定。

因此：

> Kappa 不只是看“一致”，而是看“超过随机的一致”。

---

# 5. Cohen’s Kappa 的核心思想

---

## 5.1 Kappa 衡量什么

Kappa 衡量的是：

> “超过随机一致的部分”。

公式本质：

```text
(observed agreement - random agreement)
/
(1 - random agreement)
```

意思是：

- 先计算真实一致率；
- 再扣掉随机情况下本来也会一致的部分；
- 剩下的才是真正有效的一致性。

---

## 5.2 为什么它比 accuracy 更重要

因为它考虑了：

- 标签分布；
- 随机一致；
- 类别偏斜。

所以：

在标注一致性任务中，

Kappa 通常比：

- accuracy；
- raw agreement；

更可信。

---

# 6. Kappa 分数如何解释

本轮不仅要算数字。

更重要的是：

> 解释数字。

---

## 6.1 常见经验区间

| Kappa       | 常见解释     |
| ----------- | ------------ |
| < 0         | 比随机还差   |
| 0.00 ~ 0.20 | 极低一致性   |
| 0.21 ~ 0.40 | 弱一致性     |
| 0.41 ~ 0.60 | 中等一致性   |
| 0.61 ~ 0.80 | 较高一致性   |
| 0.81 ~ 1.00 | 非常高一致性 |

注意：

这不是绝对标准。

不同任务：

- 容忍范围不同；
- 边界难度不同；
- 主观性不同。

---

## 6.2 本项目中应该怎么理解

在本项目里：

- QA span extraction：
  通常应追求较高 Kappa；

- 多轮问答：
  通常会更难；

- 文本生成质量判断：
  主观性更高，Kappa 往往更低；

- 边界样本：
  会显著拉低一致性。

---

# 7. 本轮输入数据

---

## 7.1 双人标注结果

来自：

- Day 35 的双人标注结果；
- disagreement analysis；
- 修订后的标签结构。

例如：

| sample_id | annotator_A | annotator_B |
| --------- | ----------- | ----------- |
| squad_001 | supported   | supported   |
| squad_002 | partial     | unsupported |

---

## 7.2 分歧分类结果

来自：

- `reports/day35_disagreement_analysis.csv`

---

# 8. 本轮核心任务

本轮至少完成：

1. 计算整体 Kappa；
2. 按任务类型计算；
3. 按标签计算；
4. 解释结果；
5. 找出最不稳定任务；
6. 提出修订方案。

---

# 9. 本轮执行步骤

---

## Step 1：准备统一标签数据

计算 Kappa 前必须保证：

- 标签拼写统一；
- sample_id 对齐；
- 标签没有空值；
- 两份标注长度一致。

这是很多项目最容易出错的地方。

---

## Step 2：计算整体 Kappa

先计算：

> 整个标注任务的总体一致性。

推荐使用：

```python
from sklearn.metrics import cohen_kappa_score
```

输入：

```python
labels_a = [...]
labels_b = [...]
```

输出：

```python
kappa_score
```

---

## Step 3：按任务类型分别计算

这是本轮非常重要的一步。

不要只算：

> 一个总体数字。

而是应该按：

- QA；
- 多轮问答；
- 生成质量；
- 分类；

分别计算。

因为：

不同任务稳定性完全不同。

---

## Step 4：按标签分析

进一步分析：

哪些标签最容易冲突。

例如：

| label           | disagreement_rate |
| --------------- | ----------------- |
| partial_correct | 高                |
| supported       | 低                |

这一步通常会暴露：

- 标签边界问题；
- 标签语义重叠；
- 主观性过高。

---

## Step 5：解释结果（最重要）

本轮最关键的要求：

> 不只是报数字。

而是：

> 解释为什么。

例如：

```text
多轮问答 Kappa 偏低，
主要因为：
- 指代歧义；
- 上下文不足；
- 边界样本较多。
```

或者：

```text
生成质量判断 Kappa 较低，
说明：
- 标签定义不够清晰；
- factual correctness 与 fluency 容易混淆。
```

---

# 10. Kappa 偏低时意味着什么

本轮必须理解：

> Kappa 低，
> 通常不是“模型差”。

而是：

- 规范不清；
- 标签重叠；
- 样本歧义；
- 边界样本太多；
- 标注者未对齐。

这是很多初学者最容易误解的地方。

---

# 11. 本轮重点分析方向

---

## 11.1 哪些任务最不稳定

例如：

| task_type          | kappa |
| ------------------ | ----- |
| qa_span            | 0.82  |
| multi_turn_qa      | 0.56  |
| generation_quality | 0.49  |

这能帮助你识别：

哪个任务最需要返工。

---

## 11.2 哪些标签最危险

例如：

| label             | issue           |
| ----------------- | --------------- |
| partially_correct | 边界模糊        |
| acceptable        | 与 correct 重叠 |

---

## 11.3 哪些样本拉低一致性

例如：

- 弱证据样本；
- 多义样本；
- 指代不清样本；
- 长上下文样本。

---

# 12. 提升一致性的方向

这是本轮最重要的实践部分之一。

---

## 12.1 重新写标签定义

如果两个标签长期冲突：

说明：

标签边界有问题。

---

## 12.2 增加边界样本示例

很多规范失败的原因：

是只有“标准正例”。

没有：

- hard case；
- ambiguous case；
- weak evidence case。

---

## 12.3 拆分过于含糊的标签

例如：

```text
acceptable
```

可能过于宽泛。

应该拆成：

- semantically_correct；
- partially_complete；
- weak_support。

---

## 12.4 小样本对齐

正式大规模标注前：

两位标注者应该：

- 先做一轮小样本；
- 对齐理解；
- 修正规范；
- 再正式开始。

这是工业界非常常见的流程。

---

# 13. 本轮建议的数据结构

建议输出：

| task_type | label | kappa | issue | recommendation |
| --------- | ----- | ----- | ----- | -------------- |

例如：

| generation_quality | partial | 0.41 | boundary ambiguity | split label |

---

# 14. 本轮要输出的文件

---

## 14.1 Kappa 报表

- `reports/day36_kappa_report.csv`

建议包含：

- task_type；
- label；
- kappa；
- disagreement_rate；
- issue。

---

## 14.2 Kappa 分析报告

- `reports/day36_kappa_report.md`

建议包含：

- overall Kappa；
- 各任务 Kappa；
- 各标签稳定性；
- 高风险标签；
- 高风险任务；
- 改进建议。

---

## 14.3 迭代文档

- `docs/iterations/iter_036.md`

---

# 15. 验收标准

本轮结束后，需要确认：

---

## 15.1 你是否真正理解 Kappa

不是：

> “一致率”。

而是：

> “超过随机的一致性”。

---

## 15.2 你是否知道低 Kappa 的真正原因

重点不是：

> “标注员差”。

而是：

- 标签问题；
- 样本问题；
- 规范问题；
- 边界问题。

---

## 15.3 你是否知道如何提升一致性

你应该能明确：

- 如何修规范；
- 如何修标签；
- 如何修样本；
- 如何做预对齐。

---

# 16. 本轮执行结论

---

## 16.1 结论一：Kappa 是数据质量的重要指标

它决定：

后续评测结果是否可信。

---

## 16.2 结论二：边界样本决定一致性上限

真正影响一致性的：

往往不是普通样本。

而是：

- ambiguous case；
- weak evidence；
- partially correct。

---

## 16.3 结论三：Kappa 的价值在于指导返工

它不是：

> “考试分数”。

而是：

> “规范诊断工具”。

---

# 17. 下一步计划

下一轮（Day 37）将进入：

- BLEU；
- ROUGE；
- METEOR；
- BERTScore；

正式开始：

> 自动生成质量评测。

---

# 18. 与本轮相关的后续文件

建议同步维护：

- `reports/day36_kappa_report.csv`
- `reports/day36_kappa_report.md`
- `docs/iterations/iter_036.md`
