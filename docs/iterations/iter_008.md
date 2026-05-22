# Iteration 008: 文本评测指标理解

## 概览

- **迭代名称**：文本评测指标理解
- **所属周**：Week 2 - 评测指标与自动化脚本
- **迭代编号**：Day 8
- **目标**：掌握常用文本生成与分类任务的评测指标，包括 ROUGE、BLEU、准确率和胜率；理解指标计算方法，并能手工验证小规模例子。

---

## 背景/目的

在自然语言处理 (NLP) 任务中，无论是文本生成还是文本分类，都需要评测模型输出的质量。  
通过本迭代，你将理解各种指标的原理、适用场景和计算方法，为后续自动化评测脚本开发打下基础。

---

## 解决问题

- 理解文本生成任务的常用指标：ROUGE、BLEU
- 理解分类任务的指标：准确率 (Accuracy)、胜率 (Win Rate)
- 掌握指标的公式和计算方法
- 能够通过小例子进行手工计算，验证理解正确性

---

## 参考资料

1. NLP教材相关章节：文本生成评测指标、分类评测指标
2. ROUGE 论文：[Lin, 2004, ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013/)
3. BLEU 论文：[Papineni et al., 2002, BLEU: a Method for Automatic Evaluation of Machine Translation](https://www.aclweb.org/anthology/P02-1040.pdf)
4. Python实现示例：
   - `nltk.translate.bleu_score`
   - `rouge-score` Python包
5. 网络教程和实践例子（可选）：Kaggle NLP文本生成评测

---

## 任务要求

1. 学习 ROUGE、BLEU、准确率和胜率指标的公式与计算方法
2. 能用手工方法完成小规模示例的指标计算
3. 对每个指标能够解释：
   - 含义
   - 适用场景
   - 优缺点

---

## 实现步骤

1. **阅读指标原理**
   - 阅读 ROUGE、BLEU、Accuracy、Win Rate 的公式
   - 理解每个指标如何衡量生成文本或分类输出的质量
2. **准备小规模示例**
   - 创建简单的文本生成对照或分类结果表格，例如：
     - 生成文本 vs 参考文本
     - 分类预测 vs 真实标签
3. **手工计算指标**
   - ROUGE：计算 ROUGE-N（N=1,2）和 ROUGE-L
   - BLEU：计算 unigram、bigram 等 BLEU 分数
   - Accuracy：计算预测正确率
   - Win Rate：计算在多个系统/模型间的胜率
4. **验证理解**
   - 对照 Python 计算结果，确认手算与自动化结果一致
   - 总结每个指标的适用场景和局限性

---

## 验收标准

1. 能够清晰解释 ROUGE、BLEU、Accuracy、Win Rate 的含义
2. 完成至少一个小规模手工计算示例，并验证正确性
3. 对每个指标能够指出适用场景和局限性
4. 文档记录手算过程及总结心得，可作为日后参考

---

## 附加任务（可选）

- 使用 Python 脚本实现自动化计算，并与手工结果比对
- 绘制 ROUGE/BLEU 分数随 n-gram 长度变化的曲线，以理解指标敏感性
