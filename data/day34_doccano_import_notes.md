# Day34 doccano import MVP notes

## 项目类型与 JSON 结构

- **Text Classification**：每行至少包含 `text`，可选 `label`（数组）。
  - 示例结构：`{"text": "...", "label": ["..."], "meta": {...}}`
- **Seq2Seq**：每行包含 `text`（源文本）和 `target`（目标文本）。
  - 示例结构：`{"text": "...", "target": "...", "meta": {...}}`
- **Sentence Pair**：每行包含 `text` + `text_pair`，可选 `label`。
  - 示例结构：`{"text": "...", "text_pair": "...", "label": ["..."], "meta": {...}}`

## 来自 Day31 的字段

本 MVP 仅使用 `data/day31_samples.jsonl` 前 5 条样本，并从中抽取：

- `sample_id` → `meta.sample_id`
- `source_dataset` → `meta.source_dataset`
- `input` / `question` → `text`
- `context` → `text_pair`（Sentence Pair）或 `meta.context`（Seq2Seq）
- `reference` → `target`（Seq2Seq）

## 需要 flatten 的点

Day31 是统一 schema（`input/context/question/history/reference/label`），而 doccano 导入通常按任务使用更直接字段：

- 分类任务：统一字段 flatten 为 `text` + `label`
- 生成任务：flatten 为 `text` + `target`
- 句对任务：flatten 为 `text` + `text_pair` (+ `label`)

即：将多字段通用结构映射为“按任务最小必要字段”。

## doccano 与 Label Studio 的导入差异（MVP 视角）

- **doccano**：偏向“每行一个样本”的扁平 JSON/JSONL，字段名通常直接表示任务输入（如 `text`、`text_pair`、`label`、`target`）。
- **Label Studio**：通常是 `data` + `annotations/predictions` 的嵌套结构，且与具体 labeling config 强绑定。

因此同一批 Day31 样本在 doccano 中更适合先做轻量 flatten；在 Label Studio 中通常需要按项目配置包裹成更完整对象。

## MVP 限制

- 仅提供最小可导入示例（3 条）。
- 不新增转换 pipeline。
- 不覆盖全部任务类型与边界情况。
