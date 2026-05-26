# Day 30 原始数据与统一样本组织说明

## 1. 目录用途

```text
data/day30_raw/
  squad/
  coqa/
  glue/
```

- `squad/`：存放 SQuAD 的原始结构样本与统一字段样本。
- `coqa/`：存放 CoQA 的原始结构样本与多轮对话统一字段样本。
- `glue/`：存放 GLUE 子任务（SST-2 / MRPC / MNLI）的原始结构样本与统一字段样本。

原始与整理后数据区分规则：
- `*_raw_samples.json`：尽量贴近公开数据集原始字段；
- `*_unified_samples.jsonl`：映射到项目统一 schema，供后续标注与评测流程复用。

## 2. 样本组织原则

### 2.1 为什么统一字段
SQuAD、CoQA、GLUE 的输入输出结构差异大。统一字段可让后续标注、自动指标与 judge 流程共享同一读取逻辑，避免每轮重写解析器。

### 2.2 为什么保留来源信息
统一后仍保留 `source_dataset` 与子任务信息，避免样本在混合使用时丢失语义边界（如 span 抽取 vs 分类标签）。

### 2.3 为什么区分 `task_type`
同为 NLP 任务，不同任务的评分逻辑不同：
- `qa_span_extraction` 关注证据命中；
- `multi_turn_qa` 关注对话历史依赖；
- `single_sentence_classification` / `sentence_pair_classification` / `nli_classification` 关注标签判断。

## 3. 统一字段 schema（Day 30 基线）

```json
{
  "sample_id": "string",
  "source_dataset": "string",
  "task_type": "qa_span_extraction | multi_turn_qa | single_sentence_classification | sentence_pair_classification | nli_classification",
  "input": "object",
  "context": "string|null",
  "question": "string|null",
  "reference_answer": "string|null",
  "label": "string|number|null",
  "notes": "string",
  "meta": {
    "split": "string|null",
    "raw_sample_ref": "string|null",
    "turn_id": "number|null",
    "source_license_note": "string|null"
  }
}
```

补充说明：
- `input` 保留任务原生输入结构（例如 `sentence1/sentence2`、`premise/hypothesis`、`history+question`）。
- `context/question/reference_answer/label` 作为跨任务可比字段，允许为 `null`。

## 4. 后续复用方式

这些样本将在 Day 31+ 进入以下流程：
- 标注：以 `sample_id` 为主键追加人工标注结果；
- 一致性分析：基于相同 `sample_id` 比较多标注者差异；
- 自动指标：按 `task_type` 路由到不同指标函数；
- judge 评测：统一提示模板读取 `input/context/question` 与参考输出字段。

## 5. 命名规范

### 5.1 文件命名
- 原始样本：`<dataset>_raw_samples.json`
- 统一样本：`<dataset>_unified_samples.jsonl`

### 5.2 `sample_id` 规则
- SQuAD：`squad_<split>_<index>`
- CoQA：`coqa_<story_id>_turn_<nn>`
- GLUE：`glue_<task>_<split>_<index>`

### 5.3 扩展规范
新增数据集时仅新增：
1. 数据目录；
2. 原始样本文件；
3. 统一样本文件；
4. 在 `task_type` 中声明新类型（如有必要）。

避免破坏现有字段，保持向后兼容。
