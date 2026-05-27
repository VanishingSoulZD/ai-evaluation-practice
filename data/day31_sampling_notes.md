# Day31 Sampling Notes（MVP 聚合版）

## 1) 本次目标

本次执行的是 Day31 **最小可运行聚合（MVP）**，范围仅限：

- 合并已有 processed 样本：SQuAD / CoQA / GLUE；
- 统一为轻量扁平 schema；
- 产出：
  - `data/day31_samples.jsonl`
  - `data/day31_samples.csv`
- 增加 `split` 字段：`annotation` / `dev` / `check`。

不引入新 pipeline、不新增依赖、不做通用 benchmark 框架扩展。

## 2) 输入来源

- `data/day31_samples/processed/squad_samples.jsonl`
- `data/day31_samples/processed/coqa_samples.jsonl`
- `data/day31_samples/processed/glue_samples.jsonl`

## 3) 最终轻量 schema（扁平化）

- `sample_id`
- `source_dataset`（固定为 `squad` / `coqa` / `glue`）
- `subtask`（仅 GLUE 使用，如 `sst2` / `mrpc` / `mnli`，其他为空）
- `task_type`
- `difficulty_tag`（单字符串）
- `input`
- `context`
- `question`
- `history`（JSON 字符串；无历史时为 `[]`）
- `reference`
- `label`
- `split`

## 4) 字段映射（MVP）

- `source_dataset`
  - `SQuAD` -> `squad`
  - `coqa` -> `coqa`
  - `glue_*` -> `glue`
- `subtask`
  - 从 GLUE 样本的原 `meta.subtask` 读取；
  - 非 GLUE 置空。
- `difficulty_tag`
  - 原数组取首元素（例如 `['easy'] -> 'easy'`）。
- `input/context/question`
  - QA：`input` 放问题文本，`context` 放段落上下文；
  - GLUE `text_classification`：`input` 放单句文本；
  - GLUE `sentence_pair`：`input` 放 `sentence1`，`context` 放 `sentence2`；
  - GLUE `textual_inference`：`input` 放 `premise`，`context` 放 `hypothesis`。
- `history`
  - CoQA 保留多轮历史，序列化成 JSON 字符串；
  - 其他任务为 `[]`。
- `reference/label`
  - QA：`reference` 放答案文本，`label` 置空；
  - 分类：`label` 放原数值标签（字符串），`reference` 置空。

## 5) split 规则（简单稳定）

- 使用固定顺序 + 固定比例的稳定切分：约 60% / 20% / 20%。
- split 值仅为：`annotation` / `dev` / `check`。
- CoQA 采用 conversation 绑定：同一 `source_record_id` 的多轮样本不拆分到不同 split。

## 6) 聚合结果摘要

- 总样本数：`19`
- 数据源分布：
  - `squad`: `5`
  - `coqa`: `5`
  - `glue`: `9`
- split 分布：
  - `annotation`: `13`
  - `dev`: `3`
  - `check`: `3`
- task_type 分布：
  - `qa_span`: `5`
  - `qa_dialogue`: `5`
  - `text_classification`: `3`
  - `sentence_pair`: `3`
  - `textual_inference`: `3`

## 7) 兼容后续评测链路（MVP 内）

- 保留 `task_type`，便于后续按任务路由评测逻辑；
- 保留 `subtask`（GLUE），便于子任务粒度分析；
- 保留 `split`，可直接用于 annotation/dev/check 三类流程；
- QA 与分类共用一套最小字段，避免后续脚本分支过多。
