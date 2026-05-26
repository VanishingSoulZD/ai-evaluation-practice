# Day 30 数据任务结构对比（SQuAD / CoQA / GLUE）

## 1. 文档目的

本文档用于固定 Day 30 的数据任务口径，为 Day 31+ 的标注、自动指标与 judge 评测提供统一输入规范。重点是任务结构对齐，不涉及模型训练与 benchmark 运行。

---

## 2. 数据集定位

| 数据集 | 定位 | 任务形态 | 核心关注 |
|---|---|---|---|
| SQuAD | 阅读理解基准 | 单轮 QA（span 抽取） | 证据定位与答案命中 |
| CoQA | 对话式阅读理解 | 多轮 QA（上下文依赖） | 对话记忆与语境承接 |
| GLUE | 通用语言理解任务集合 | 分类/匹配/蕴含等判别任务 | 语义判断与泛化理解 |

---

## 3. 输入结构对比

### 3.1 SQuAD
- 输入主结构：`context + question`
- 上下文：单段文本
- 交互轮次：单轮
- 典型字段：`id`, `title`, `context`, `question`, `answers`

### 3.2 CoQA
- 输入主结构：`story + conversation_history + current_question`
- 上下文：故事文本 + 前序 QA 历史
- 交互轮次：多轮
- 典型字段：`id`, `story`, `questions[]`, `answers[]`, `turn_id`

### 3.3 GLUE
GLUE 是任务集合，不同子任务输入不同：
- SST-2：`sentence`
- MRPC：`sentence1 + sentence2`
- MNLI：`premise + hypothesis`

---

## 4. 输出结构对比

| 数据集 | 输出形式 | 字段特征 | 评分取向 |
|---|---|---|---|
| SQuAD | span / 文本答案 | `answers.text`, `answers.answer_start` | 是否命中证据片段 |
| CoQA | 自由文本答案（按轮次） | 每轮 `answer`，依赖历史语境 | 语境一致与多轮正确性 |
| GLUE | 离散标签 | 二分类或三分类标签 | 分类准确率/相关判别指标 |

---

## 5. 适合评测的能力维度

### 5.1 SQuAD
- Evidence grounding（证据落点）
- Question-context alignment（问题与段落对齐）
- Extractive QA 命中能力

### 5.2 CoQA
- Multi-turn memory（多轮记忆）
- Coreference/anaphora resolution（指代消解）
- Context carry-over（上下文承接）

### 5.3 GLUE（以 SST-2 / MRPC / MNLI 为代表）
- Semantic classification（语义分类）
- Semantic matching（语义匹配/复述识别）
- Entailment reasoning（蕴含/矛盾判断）

---

## 6. 统一 schema 设计（项目基线）

为兼容 QA、多轮 QA、分类与匹配任务，采用以下统一字段：

- `sample_id`
- `source_dataset`
- `task_type`
- `input`
- `context`
- `question`
- `reference_answer`
- `label`
- `notes`
- `meta`（扩展：`split`, `raw_sample_ref`, `turn_id` 等）

### 6.1 字段映射示意

| 统一字段 | SQuAD | CoQA | GLUE |
|---|---|---|---|
| `task_type` | `qa_span_extraction` | `multi_turn_qa` | `single_sentence_classification` / `sentence_pair_classification` / `nli_classification` |
| `input` | `{context, question}` | `{story, history, question}` | `{sentence}` / `{sentence1, sentence2}` / `{premise, hypothesis}` |
| `reference_answer` | span 文本 | 当前轮参考答案 | `null` |
| `label` | `null` | `null` | 任务标签 |

---

## 7. 后续评测链路映射

| 链路 | SQuAD | CoQA | GLUE |
|---|---|---|---|
| 人工标注 | ✅ 证据支撑与答案准确性 | ✅ 多轮一致性与承接 | ✅ 标签边界与语义判断 |
| 自动指标 | ✅ EM/F1 类抽取指标 | ✅ 轮次级准确率/一致性统计 | ✅ Accuracy/F1/MCC(视任务) |
| Judge 评测 | ✅ 答案是否被上下文支持 | ✅ 是否利用历史并保持一致 | ✅ 推理与标签判定解释性 |
| 一致性分析 | ✅ 多标注者 span 边界一致性 | ✅ 轮次历史依赖一致性 | ✅ 标签判定一致性 |

---

## 8. Day 30 结论

1. 三类数据集覆盖了后续评测所需的核心任务形态：单轮 QA、多轮 QA、判别式 NLU。
2. 统一 schema 已满足当前项目最小可扩展需求，且不引入复杂 ETL。
3. Day 31+ 可在不改数据主结构的前提下，直接追加标注字段与评测结果字段。
