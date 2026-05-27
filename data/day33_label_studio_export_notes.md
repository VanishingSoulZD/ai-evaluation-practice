# Day33 Label Studio 导出说明（MVP）

## 1) 导出文件结构
- 文件：`outputs/day33_label_studio_export.sample.json`
- 顶层是任务数组，每个 task 至少包含：
  - `id`
  - `data`
  - `meta`
  - `annotations`
- `annotations` 内每条标注包含 `result` 数组。

## 2) result 解析方式
在 `annotations[*].result[*]` 中按 `from_name` 取值（固定命名）：
- `label` -> `value.choices[0]`
- `final_answer` -> `value.text[0]`
- `evidence_span` -> `value.text[0]`
- `rule_id` -> `value.text[0]`

## 3) 如何取最终 label
MVP 规则：
1. 过滤 `was_cancelled=true` 的 annotation；
2. 取 `updated_at` 最新的一条 annotation；
3. 从该 annotation 的 `result` 中解析 `label`。

## 4) 如何保留 sample_id / task_type
采用双保留：
- `data.sample_id` 与 `meta.sample_id`
- `data.task_type` 与 `meta.task_type`

这样可同时满足：
- 标注界面展示与导出回连（data）；
- 后处理脚本路由与兼容（meta）。

## 5) 后续脚本强依赖字段
- 样本定位：`sample_id`, `task_type`, `source_dataset`
- 标注输出：`label`, `final_answer`, `evidence_span`, `rule_id`

## 6) 当前 MVP 限制
- 仅提供最小示例，不代表真实 Label Studio 全字段导出。
- 仅覆盖 `qa_span` + `classification` 两类任务示例。
- 未实现完整 normalize / 评测 pipeline。
