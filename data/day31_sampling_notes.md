# Day31 Sampling Notes（SQuAD 小样本抽取）

## 1) 本次范围

- 仅处理 **SQuAD**。
- 不处理 CoQA。
- 不处理 GLUE。
- 仅抽取少量样本（5 条），用于 Day31 schema 对齐与格式验证。

## 2) 抽样方式

- 来源：`data/day30_raw/squad/squad_raw_samples.json`。
- 方式：只读取前 N 条（N=5），不做全量遍历。
- 原则：保持原始问答语义，不改写 context/question/reference answer。

## 3) 统一 Schema 映射

每条样本均包含以下核心字段：

- `sample_id`
- `source_dataset`
- `input`
- `reference`
- `task_type`
- `difficulty_tag`

并补充：

- `source_split`
- `meta`（含 `source_record_id`）

SQuAD 映射规则：

- `task_type` 固定为 `qa_span`。
- `input.context` = 原始 `context`。
- `input.question` = 原始 `question`。
- `reference.answer_text` = 原始 `answers.text[0]`。
- `difficulty_tag` 为工作标签（初版人工标注）：
  - 前 3 条设为 `easy`（答案边界直接、定位清晰）；
  - 后 2 条设为 `medium`（需要轻度语义定位）。

## 4) 输出文件

- 原始裁剪样本：`data/day31_samples/raw/squad_samples.json`
- 统一格式（主输入）：`data/day31_samples/processed/squad_samples.jsonl`
- 人工检查表：`data/day31_samples/processed/squad_samples.csv`

## 5) 一致性说明（JSONL vs CSV）

两者保持一一对应（5 条）：

- `sample_id` 一致；
- `context/question/reference answer` 一致；
- `task_type` 一致（`qa_span`）；
- `difficulty_tag` 在 JSONL 为数组，在 CSV 中用 `|` 拼接字符串表示。

## 6) 后续建议

- Day32 可在当前映射模板下扩展 CoQA 与 GLUE。
- 扩展时保持 `task_type` 与 `reference` 语义优先，不做“字段硬压平”。
