# Iteration 009: Python 实现文本评测指标

## 概览

- **迭代名称**：Python 实现指标
- **所属周**：Week 2 - 评测指标与自动化脚本
- **迭代编号**：Day 9
- **目标**：掌握如何用 Python 实现常用文本生成与分类任务的评测指标，包括 ROUGE、BLEU、Accuracy、Win Rate，并验证计算结果与手工计算一致。

---

## 背景/目的

在 Day 8 中，我们理解了 ROUGE、BLEU、Accuracy、Win Rate 的公式和手算方法。  
本迭代旨在将这些指标用 Python 函数实现，实现自动化计算，为后续评测脚本开发打基础。

---

## 解决问题

- 理解如何用 Python 实现文本生成任务的指标 ROUGE、BLEU
- 实现分类任务指标 Accuracy、Win Rate
- 学会使用 Python 库（NLTK、rouge-score）以及纯 Python 方法
- 输出结果与手工计算示例一致，保证可复现性

---

## 参考资料

1. NLTK 官方文档：`nltk.translate.bleu_score`
2. rouge-score 官方文档：`rouge_score` Python 包
3. Python 标准库：`collections.Counter`、`math` 等
4. Day 8 手工计算示例作为参考
5. 网络教程：Kaggle NLP 文本评测指标实现示例

---

## 任务要求

1. 使用 Python 编写函数计算以下指标：
   - ROUGE-N（N=1,2）和 ROUGE-L
   - BLEU（unigram、bigram）
   - Accuracy（准确率）
   - Win Rate（胜率）
2. 函数应支持小规模示例输入：
   - 文本生成示例：参考文本与候选文本
   - 分类示例：真实标签与预测标签
3. 输出结果应与 Day 8 手工计算结果一致
4. 可选：同时实现纯 Python 和库函数两种方式，进行对比验证

---

## 实现步骤

1. **导入小样本数据**
   - 文本生成：
     ```python
     ref = "the cat is on the mat"
     cand = "the cat sat on the mat"
     ```
   - 分类任务：
     ```python
     y_true = [1, 0, 1, 1, 0, 0, 1, 0]
     y_pred = [1, 1, 1, 1, 0, 0, 0, 0]
     ```
   - 对战胜率：
     ```python
     wins, losses, ties = 6, 3, 1
     ```
2. **编写指标函数**
   - ROUGE-N / ROUGE-L 函数
   - BLEU 函数（可调用 NLTK 或手动实现）
   - Accuracy 函数
   - Win Rate 函数（支持平局折半选项）
3. **计算指标**
   - 调用上述函数计算小样本的指标值
4. **输出结果**
   - 输出结果应与手算值对比验证
   - 确保结果可复现，记录四舍五入精度
5. **可选扩展**
   - 对比纯 Python 与库函数结果
   - 记录函数接口和使用说明，便于后续评测脚本复用

---

## 验收标准

1. Python 函数正确实现 ROUGE、BLEU、Accuracy、Win Rate
2. 输出结果与 Day 8 手工计算示例一致
3. 函数接口清晰，可复用
4. 输出结果可直接用于后续自动化评测脚本

---

## 附加任务（可选）

- 封装成 Python 模块 `metrics.py`，支持批量数据输入
- 可接受多个参考文本（multi-reference）计算 ROUGE/BLEU
- 输出详细对比表，包括手算 vs Python 结果
