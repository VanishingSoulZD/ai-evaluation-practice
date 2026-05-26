# Iteration 029 — 确定本轮项目主题与任务边界

## 1. 本次迭代目标

本轮的目标不是开始写模型评测代码，而是先把**评测对象、任务边界、数据来源、最终交付物**定义清楚，避免后续迭代过程中频繁改题、改口径、改数据结构。

本轮最终要确认的是：

- 本轮主线为 **文本生成 + 问答评测**；
- 子任务拆分为：
  - **子任务 A**：SQuAD / CoQA 风格的问答评测；
  - **子任务 B**：生成任务的自动指标评测（BLEU / ROUGE / METEOR / BERTScore）；

- 最终交付物包括：
  - 一个主数据集样本集；
  - 一份标注规范；
  - 一份双人标注一致性分析；
  - 一套自动指标脚本；
  - 一份 judge 评测说明；
  - 一份完整报告。

---

## 2. 本轮任务边界

### 2.1 不做什么

本轮不做以下内容：

- 不做纯分类项目；
- 不做没有真实数据来源的“自造样本”演示；
- 不做只看单一指标的片面评测；
- 不把项目做成只验证代码能跑的玩具流程。

### 2.2 本轮做什么

本轮只做一条可复用的评测链路：

1. 从主流公开数据集中抽样；
2. 建立统一的数据格式；
3. 写出可执行的标注规范；
4. 为后续标注、一致性分析、自动指标和 judge 评测做准备；
5. 最终形成一个能支持问答、摘要、改写、对话等生成式任务的评测框架雏形。

---

## 3. 任务选择依据

本轮选择“文本生成 + 问答评测”作为主线，原因如下：

1. **可扩展性强**
   - 问答、摘要、改写、对话都属于生成式任务；
   - 一条成熟的生成式评测链路，后续可以迁移到更多场景。

2. **链路完整**
   - 问答任务天然包含上下文、问题、参考答案、模型回答；
   - 适合同时练习人工标注、自动指标和 judge 评测。

3. **适合做真实项目**
   - 这类任务在实际业务里很常见；
   - 结果容易做成报告，也容易解释。

4. **便于统一方法论**
   - 数据层可以用 SQuAD / CoQA；
   - 任务层可以用 BLEU / ROUGE / METEOR / BERTScore；
   - 评估层可以进一步扩展到 OpenCompass / MT-Bench / FastChat 风格的 judge。

---

## 4. 主流外部资源

本轮只保留与任务直接相关、且后续迭代会实际用到的官方入口。

### 4.1 数据集

- SQuAD：[https://rajpurkar.github.io/SQuAD-explorer/](https://rajpurkar.github.io/SQuAD-explorer/)
- GLUE：[https://gluebenchmark.com/](https://gluebenchmark.com/)
- CoQA：[https://stanfordnlp.github.io/coqa/](https://stanfordnlp.github.io/coqa/)

### 4.2 标注工具

- Label Studio：[https://labelstud.io/](https://labelstud.io/)
- Label Studio 文档：[https://labelstud.io/guide/](https://labelstud.io/guide/)
- doccano：[https://doccano.github.io/doccano/](https://doccano.github.io/doccano/)
- doccano tutorial：[https://doccano.github.io/doccano/tutorial/](https://doccano.github.io/doccano/tutorial/)

### 4.3 一致性与评测

- OpenCompass：[https://opencompass.org.cn/](https://opencompass.org.cn/)
- OpenCompass LLM judge 文档：[https://doc.opencompass.org.cn/advanced_guides/llm_judge.html](https://doc.opencompass.org.cn/advanced_guides/llm_judge.html)
- MT-Bench 论文：[https://arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)
- FastChat：[https://github.com/lm-sys/fastchat](https://github.com/lm-sys/fastchat)
- Chatbot Arena：[https://lmarena.ai/](https://lmarena.ai/)

### 4.4 自动指标

- BLEU 论文：[https://aclanthology.org/P02-1040/](https://aclanthology.org/P02-1040/)
- ROUGE 论文：[https://aclanthology.org/W04-1013/](https://aclanthology.org/W04-1013/)
- METEOR 论文：[https://aclanthology.org/W05-0909/](https://aclanthology.org/W05-0909/)
- BERTScore：[https://github.com/Tiiiger/bert_score](https://github.com/Tiiiger/bert_score)

---

## 5. 本轮统一的数据与任务定义

### 5.1 主线定义

本轮的主线定义为：

> **面向问答和文本生成任务的评测基础链路搭建**

### 5.2 子任务 A：问答评测

问答评测部分主要参考 SQuAD / CoQA 的任务结构，关注以下能力：

- 模型是否理解上下文；
- 模型是否能准确找到答案；
- 对多轮上下文是否有记忆和承接能力；
- 生成答案是否与参考答案一致或语义等价。

### 5.3 子任务 B：生成任务自动指标评测

生成任务评测部分主要使用以下指标：

- BLEU：偏字面匹配；
- ROUGE：偏内容覆盖；
- METEOR：偏更接近人工判断的词级匹配；
- BERTScore：偏语义级相似度。

### 5.4 后续可扩展方向

本轮完成后，链路可以自然扩展到：

- 摘要任务；
- 改写任务；
- 多轮对话任务；
- 偏好比较任务；
- judge 评测任务。

---

## 6. 本轮最终交付物定义

### 6.1 数据层交付物

- `data/day29_project_scope.md`
- 后续可复用的样本组织方式
- 主数据集样本集的定义说明

### 6.2 标注层交付物

- 一份标注规范
- 一份人工标注流程说明
- 一份双人标注一致性分析

### 6.3 指标层交付物

- 一套自动指标脚本
- 指标结果表
- 指标解释文档

### 6.4 judge 层交付物

- 一份 judge 评测说明
- LLM-as-a-judge 的适用场景说明
- 对 OpenCompass / MT-Bench / FastChat 的参考整理

### 6.5 报告层交付物

- 一份完整报告
- 图表和结论
- 局限性与下一步计划

---

## 7. 本次迭代的执行结论

### 7.1 结论一：项目不是分类，而是生成式评测链路

本轮已经确认，项目后续不是只围绕分类任务展开，而是围绕**生成式评测链路**展开。这样设计的好处是：

- 可以同时覆盖问答、摘要、改写、对话等多个任务；
- 可以同时练习人工标注和自动指标；
- 可以自然过渡到 LLM judge 评测。

### 7.2 结论二：任务边界要前置固定

本轮确认后，后面的迭代不再临时换题。后续所有 Day 30 ~ Day 42 的工作，都围绕本轮定义的主线展开。

### 7.3 结论三：数据源必须来自主流公开基准

后续样本优先从 SQuAD、CoQA、GLUE 等主流数据集中抽取，不再使用自行生成样本作为主样本来源。这样做可以保证：

- 任务定义清晰；
- 数据格式稳定；
- 评测结果更容易解释；
- 后续可与公开 benchmark 接轨。

---

## 8. 本轮产出文件

### 已确认需要创建的文件

- `docs/iterations/iter_029.md`
- `docs/practice_plan.md`
- `data/day29_project_scope.md`

### 建议的后续文件命名

- `docs/iterations/iter_030.md`
- `docs/iterations/iter_031.md`
- `docs/iterations/iter_032.md`
- ...
- `docs/iterations/iter_042.md`

---

## 9. 下一步计划

下一轮将进入 Day 30，开始对 SQuAD、GLUE、CoQA 的数据结构做系统梳理，并把后续样本抽取的目标格式固定下来。
