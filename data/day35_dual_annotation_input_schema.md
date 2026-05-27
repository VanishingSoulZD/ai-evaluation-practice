# Day35 Task 1 — 双人标注结果最小输入 Schema（MVP）

## 1. Background

- Day35 的目标是让“双人标注结果”可稳定进入分歧分析流程。
- 本文档定义最小输入 Schema，保证：
  - 两份独立标注可对齐；
  - 标签可统一；
  - 缺失/重复可被显式发现；
  - Day36 的 Kappa 计算有可用输入。
- 本文档是 **数据输入规范**，不包含脚本实现。

## 2. Design Goals (MVP)

- 最小可执行：字段尽量少，但能支撑对齐与质量检查。
- 明确约束：必填、可选、取值范围、异常处理要可落地。
- 不引入复杂结构：不设计数据库、不引入平台耦合字段。
- 可扩展：后续可追加字段，不破坏 MVP 主流程。

## 3. Minimal Schema

### 3.1 Canonical Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `sample_id` | string | Yes | 样本唯一 ID，对齐主键的一部分。 |
| `annotator` | string | Yes | 标注者标识（如 `A`/`B` 或匿名 ID）。 |
| `label` | string | Yes | 主标签，仅允许规定标签集合。 |
| `round` | string | Yes | 标注轮次（如 `iter035_r1`）。 |
| `task_type` | string | No (Recommended) | 任务类型（如 `qa_span`），用于分层分析。 |
| `rule_id` | string | No (Recommended) | 规则编号，便于分歧归因。 |
| `decision_status` | string | No (Recommended) | `FINAL` 或 `NEED_ADJUDICATION`。 |

### 3.2 Minimal Required Set

最小必填集合：

- `sample_id`
- `annotator`
- `label`
- `round`

> 若缺少上述任一字段，记录不应进入分歧分析或 Kappa 输入集合。

## 4. Field Constraints

### 4.1 `sample_id`

- 必须与 Day31 样本中的 `sample_id` 一致。
- 不允许重编码（如改前缀、改大小写、加额外后缀）。
- 不允许为空字符串。

### 4.2 `annotator`

- 同一轮双人标注必须能唯一标识两个标注者。
- 推荐值：
  - 展示层：`A`、`B`
  - 存储层：`ann_01`、`ann_02`
- 同一个人跨批次应保持稳定 ID。

### 4.3 `label`

- 必须使用且仅使用以下集合：
  - `SUPPORTED`
  - `UNSUPPORTED`
  - `MULTI_ANSWER`
  - `AMBIGUOUS_SPAN`
- 强制大写（uppercase enforcement）。
- 空标签（空字符串/NULL）视为无效记录状态，不可直接入分析集合。

### 4.4 `round`

- 推荐格式：`iterXXX_rY`（如 `iter035_r1`）。
- 作用：区分返工重标、避免旧记录与新记录混用。

### 4.5 `task_type`（可选）

- 推荐填写，例如：`qa_span`。
- 用于后续按任务类型切分一致性分析。

### 4.6 `rule_id`（可选）

- 推荐填写规则编号（如 `RC-8.1-R3`）。
- 用于分歧归因，不作为 Kappa 必要字段。

### 4.7 `decision_status`（可选）

- 允许值：
  - `FINAL`
  - `NEED_ADJUDICATION`
- `NEED_ADJUDICATION` 记录不得直接进入最终 Kappa 计算集合。

## 5. sample_id Alignment Rules

对齐以 `(sample_id, round)` 为核心键，步骤如下：

1. 验证双方记录使用同一 `round`。
2. 用 `sample_id` 对齐两位标注者记录。
3. 生成三类结果：
   - `both_present`：双方都有有效记录；
   - `missing_in_A`：B 有但 A 无；
   - `missing_in_B`：A 有但 B 无。
4. 仅 `both_present` 且标签有效的记录可进入一致性主集合。

## 6. Annotator Naming Strategy

- 目标：可追踪、去敏感、跨轮次稳定。
- 规范：
  - 分析文件中使用 `A`/`B` 或匿名 ID。
  - 不使用真实姓名、邮箱、工号。
  - 若存在映射关系（例如 `A -> ann_01`），映射表应在受控位置单独管理，不混入分析输入文件。

## 7. Label Normalization Strategy

规范化必须在分析前完成。

### 7.1 Normalization Rules

- 去除首尾空白。
- 统一为大写。
- 可选地将已知别名映射到标准值（例如 `supported -> SUPPORTED`）。
- 规范化后必须落在合法集合内。

### 7.2 Illegal Label Rejection

以下任一情况判定为非法标签：

- 不在允许集合；
- 为空；
- 拼写错误或自定义新标签。

非法标签记录：

- 不得直接进入分歧分析主集合；
- 不得直接进入 Kappa 输入集合；
- 必须进入数据质量问题清单。

## 8. Missing Data Handling

必须区分两类缺失：

1. **Missing sample**：某标注者不存在该 `sample_id` 记录。
2. **Empty label**：存在 `sample_id`，但 `label` 为空或无效。

处理规则：

- 两类缺失都 **不得直接进入 Kappa**。
- 两类缺失都应单独统计并输出 coverage。
- coverage 定义：

`coverage = 双方都有有效标签的 sample 数 / 目标 sample 总数`

- 当 coverage 低于预设阈值（阈值由流程方定义）时，应先补标再做正式一致性评估。

## 9. Duplicate Record Handling

### 9.1 Duplicate Key

重复键定义为：

- `(sample_id, annotator, round)`

### 9.2 Policy

- 重复记录属于数据质量问题。
- 重复记录 **不得静默自动消解**（例如“默认取最后一条”）。
- 重复记录必须进入人工核查或显式规则处理流程。
- 在核查完成前，该键对应记录不应进入 Kappa 输入集合。

## 10. Recommended CSV Example

```csv
sample_id,annotator,label,round,task_type,rule_id,decision_status
squad_train_0001,A,UNSUPPORTED,iter035_r1,qa_span,RC-8.1-R3,FINAL
squad_train_0001,B,SUPPORTED,iter035_r1,qa_span,RC-8.1-R1,FINAL
squad_train_0002,A,AMBIGUOUS_SPAN,iter035_r1,qa_span,RC-8.1-R4,NEED_ADJUDICATION
squad_train_0002,B,AMBIGUOUS_SPAN,iter035_r1,qa_span,RC-8.1-R4,NEED_ADJUDICATION
squad_train_0003,A,MULTI_ANSWER,iter035_r1,qa_span,RC-8.1-R2,FINAL
squad_train_0003,B,MULTI_ANSWER,iter035_r1,qa_span,RC-8.1-R2,FINAL
```

说明：

- 示例仅使用允许标签集合。
- `decision_status=NEED_ADJUDICATION` 的记录示例化保留，但不直接入 Kappa。

## 11. Recommended JSONL Example

```jsonl
{"sample_id":"squad_train_0001","annotator":"A","label":"UNSUPPORTED","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R3","decision_status":"FINAL"}
{"sample_id":"squad_train_0001","annotator":"B","label":"SUPPORTED","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R1","decision_status":"FINAL"}
{"sample_id":"squad_train_0002","annotator":"A","label":"AMBIGUOUS_SPAN","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R4","decision_status":"NEED_ADJUDICATION"}
{"sample_id":"squad_train_0002","annotator":"B","label":"AMBIGUOUS_SPAN","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R4","decision_status":"NEED_ADJUDICATION"}
{"sample_id":"squad_train_0003","annotator":"A","label":"MULTI_ANSWER","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R2","decision_status":"FINAL"}
{"sample_id":"squad_train_0003","annotator":"B","label":"MULTI_ANSWER","round":"iter035_r1","task_type":"qa_span","rule_id":"RC-8.1-R2","decision_status":"FINAL"}
```

## 12. Risks and Mitigations

- ID 漂移风险（`sample_id` 被平台导出改写）
  - 缓解：导入前做 ID 格式一致性检查；不一致直接阻断。
- 标签漂移风险（同义词、大小写、拼写）
  - 缓解：分析前强制 normalization + 非法标签拦截。
- 缺失掺入风险（把缺失当作分歧）
  - 缓解：先分离 coverage 统计，再做一致性计算。
- 重复静默覆盖风险
  - 缓解：禁止自动“取最后一条”，必须显式核查。
- 轮次污染风险（返工前后混用）
  - 缓解：`round` 必填，并以 `(sample_id, round)` 对齐。

## 13. Downstream Compatibility (Day36 Kappa)

### 13.1 Kappa-ready Subset Definition

可进入 Day36 Kappa 的记录应同时满足：

- `sample_id` 非空且双方可对齐；
- `annotator` 可区分为两位独立标注者；
- `label` 已规范化且在允许集合内；
- `round` 一致；
- 无重复键冲突；
- 非缺失样本、非空标签；
- `decision_status` 若存在，应为 `FINAL`。

### 13.2 Non-Kappa Records

以下记录不进入 Kappa：

- 缺失样本；
- 空标签或非法标签；
- 重复键未核查完成；
- `decision_status=NEED_ADJUDICATION`。

### 13.3 Definition of Ready for Day36

当且仅当以下条件满足，可进入 Day36：

- schema 校验通过；
- 标签规范化完成；
- 缺失/重复问题已出具清单；
- Kappa-ready 子集可稳定导出；
- coverage 已单独报告。

---

## Appendix A — Standalone Checklist

- 字段命名在全文一致：`sample_id`, `annotator`, `label`, `round`, `task_type`, `rule_id`, `decision_status`。
- 标签仅包含：`SUPPORTED`, `UNSUPPORTED`, `MULTI_ANSWER`, `AMBIGUOUS_SPAN`。
- 重复键定义固定为：`(sample_id, annotator, round)`。
- 缺失与空标签已区分并给出独立处理策略。
- CSV/JSONL 示例与字段定义一致。
- 未引用任何不存在脚本或额外文件。
