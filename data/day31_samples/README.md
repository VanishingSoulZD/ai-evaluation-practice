# Day31 样本目录与统一 Schema 定义

本文件定义 Day31 的样本组织方式与统一字段标准。当前阶段仅完成结构设计，不进行大规模抽样、不编写评测代码。

## 1) 统一 Schema

建议每条样本使用同一 JSON 结构（JSONL 每行一条）：

```json
{
  "sample_id": "squad_train_0001",
  "source_dataset": "squad",
  "source_split": "train",
  "task_type": "qa_span",
  "difficulty_tag": ["medium"],
  "input": {
    "context": "...",
    "question": "...",
    "history": []
  },
  "reference": {
    "answer_text": "...",
    "label": null,
    "meta": {}
  },
  "meta": {
    "source_record_id": "...",
    "notes": ""
  }
}
```

> 说明：
> - `input.history` 主要用于多轮问答（如 CoQA），单轮任务可为空数组。
> - `reference.answer_text` 与 `reference.label` 二选一为主：问答/生成任务用 `answer_text`，分类任务用 `label`。

---

## 2) `sample_id` 规范

`sample_id` 必须全局唯一、可读、可追踪，推荐格式：

`{dataset}_{split}_{index4}`

示例：

- `squad_train_0001`
- `coqa_dev_0003`
- `glue_mnli_train_0012`

规范要求：

1. 全小写；
2. 使用下划线分隔；
3. 最后一段为固定 4 位流水号；
4. 如需包含子任务（如 GLUE），放在 dataset 段中体现（例如 `glue_mnli`）。

---

## 3) `task_type` 定义

Day31 统一使用以下任务类型枚举：

- `qa_span`：抽取式问答（如 SQuAD）。
- `qa_dialogue`：多轮对话问答（如 CoQA）。
- `text_classification`：单文本分类。
- `sentence_pair`：句对关系判断（相似度/匹配/蕴含前置表示）。
- `textual_inference`：文本蕴含（NLI）任务。

使用规则：

- 优先选择“最贴近原任务语义”的类型；
- 一个样本仅标注一个主 `task_type`；
- 后续若扩展新任务类型，需在本文件追加定义并保持向后兼容。

---

## 4) `difficulty_tag` 定义

`difficulty_tag` 采用“可多标签”数组，当前预设：

- `easy`：信息直接、答案边界清晰。
- `medium`：需要轻度推理或跨句定位。
- `hard`：需要复杂推理、干扰项多。
- `ambiguous`：题面或参考答案存在歧义风险。
- `multi_hop`：需要多跳信息整合。

标注建议：

- 至少 1 个标签；
- 若存在歧义或多跳，允许和难度标签并存（如 `[
  "hard", "multi_hop"
]`）；
- 初期由抽样人给出“工作标签”，后续可在标注阶段复核。

---

## 5) 目录用途

Day31 目录结构如下：

```text
data/day31_samples/
  raw/         # 原始拷贝或最小裁剪中间件（保持来源可追踪）
  processed/   # 统一 schema 后的样本文件（后续主输入）
  split/       # 按 annotation/dev/check 划分后的样本清单
  README.md    # 本说明文档
```

用途约定：

- `raw/`：尽量不改语义，只做最小字段映射准备；
- `processed/`：统一结构后的“单一事实来源”；
- `split/`：面向流程使用场景进行切分（不是按数据集切分）。

---

## 6) 后续复用方式

该结构后续复用路径：

1. **标注阶段**：`split/annotation.*` 作为人工标注入口；
2. **开发阶段**：`split/dev.*` 作为脚本调试与 schema 校验集；
3. **检查阶段**：`split/check.*` 作为流程健康检查与回归最小集；
4. **评测阶段**：默认读取 `processed/`，再按 `split/` 路由不同用途。

本轮（Day31）仅确定规范，不强制产出大规模样本文件。
