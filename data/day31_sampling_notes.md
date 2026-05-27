# Day31 Sampling Notes（CoQA 小样本抽取）

## 1) 本次范围

- 仅处理 **CoQA**。
- 当前不处理 SQuAD。
- 当前不处理 GLUE。
- 仅抽取少量样本（5 条），用于 Day31 schema 对齐与多轮对话结构验证。

## 2) 抽样方式

- 来源：`data/day30_raw/coqa/coqa_raw_samples.json`。
- 方式：只读取前 N 条（N=1 条对话记录），并从该记录前 5 个 turn 构造 5 条样本；不做全量遍历。
- 原则：保持原始 story、question、answer 语义；保留多轮历史。

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
- `meta`（含 `source_record_id`、`turn_id`）

CoQA 映射规则：

- `task_type` 固定为 `qa_dialogue`。
- `input.context` = 原始 `story`。
- `input.question` = 当前轮问题。
- `input.history` = 当前轮之前所有 `{turn_id, question, answer}` 顺序列表。
- `reference.answer_text` = 当前轮答案文本。
- `difficulty_tag` 为工作标签（初版人工标注）：
  - 前 3 条设为 `easy`；
  - 后 2 条设为 `medium`（需要更明显的上下文依赖/因果理解）。

## 4) 输出文件

- 原始裁剪样本：`data/day31_samples/raw/coqa_samples.json`
- 统一格式（主输入）：`data/day31_samples/processed/coqa_samples.jsonl`
- 人工检查表：`data/day31_samples/processed/coqa_samples.csv`

## 5) 一致性说明（JSONL vs CSV）

两者保持一一对应（5 条）：

- `sample_id` 一致；
- `context/question/reference answer` 一致；
- `task_type` 一致（`qa_dialogue`）；
- `history` 在 JSONL 为结构化数组，在 CSV 中序列化为 JSON 字符串。

## 6) 对话历史组织说明

- 每一条样本表示一个 turn 的“当前问题”。
- `input.history` 仅包含历史轮次（不含当前轮）。
- 历史按 `turn_id` 升序排列，保证可重建完整对话轨迹。
