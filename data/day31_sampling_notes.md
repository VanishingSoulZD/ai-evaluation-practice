# Day31 Sampling Notes（GLUE 小样本抽取）

## 1) 本次范围

- 仅处理 **GLUE**。
- 当前不处理 SQuAD。
- 当前不处理 CoQA。
- 抽取少量样本（共 9 条），用于 Day31 统一 schema 的分类任务适配验证。

## 2) 抽样方式

- 来源：`data/day30_raw/glue/glue_raw_samples.json`。
- 方式：每个子任务只读取前 N 条（N=3），不做全量遍历，不下载完整 GLUE。
- 本次选取 3 个子任务：`sst2`、`mrpc`、`mnli`。

## 3) 子任务与 task_type 映射

- `sst2` -> `text_classification`（单句情感分类）
- `mrpc` -> `sentence_pair`（句对等价判断）
- `mnli` -> `textual_inference`（前提-假设蕴含关系）

## 4) 统一 Schema 如何兼容分类任务

统一结构保持不变：

- `input` 作为任务输入容器，按子任务放入对应字段：
  - sst2：`input.text`
  - mrpc：`input.sentence1` + `input.sentence2`
  - mnli：`input.premise` + `input.hypothesis`
- `reference.label` 存放原始数值标签；
- `reference.meta.label_text` 存放语义标签文本；
- `reference.meta.label_map` 保留该子任务全部标签语义映射。

这样既保留统一接口（所有任务都有 `input/reference`），也不损失各分类子任务的输入结构差异。

## 5) 标签组织（保留原始语义）

- SST-2：`0=negative`, `1=positive`
- MRPC：`0=not_equivalent`, `1=equivalent`
- MNLI：`0=entailment`, `1=neutral`, `2=contradiction`

每条样本同时保留：

1. 原始整数标签（`reference.label`）；
2. 当前标签语义（`reference.meta.label_text`）；
3. 全量标签字典（`reference.meta.label_map`）。

## 6) 输出文件

- 原始裁剪：`data/day31_samples/raw/glue_samples.json`
- 统一样本（JSONL）：`data/day31_samples/processed/glue_samples.jsonl`
- 人工检查（CSV）：`data/day31_samples/processed/glue_samples.csv`
