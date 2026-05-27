# Day34 doccano Mapping MVP

## 1. 背景与目标

- Day31：已完成样本统一，形成统一 `task_type` 与基础字段结构。
- Day32：已定义可执行标注规范与标签口径。
- Day33：已完成 Label Studio MVP 闭环。
- 本文档目标：为 Day34 的 doccano 实操提供最小映射依据，确保任务路由稳定、标签一致、导出可复用。

---

## 2. 映射原则

- **最小闭环优先**：先保证“可导入 → 可标注 → 可导出”的最小链路，不扩展复杂流程。
- **单项目单职责**：一个项目只解决一种核心标注目标，避免字段与流程过载。
- **标签与 Day32 对齐**：标签集合与定义不新增、不改名，避免口径漂移。
- **保留 `sample_id`**：全过程保留主键，确保导出后可追溯、可 join、可复核。

---

## 3. `task_type` → doccano project type 映射表

| task_type | doccano type | MVP 是否纳入 | 原因 |
| --------- | ------------ | ----------- | ---- |
| `qa_span` | `Seq2Seq`（主） + `Text Classification`（辅） | 是 | `qa_span` 需要“答案产出 + 支持性判断”，单一项目难覆盖；MVP 采用双项目拆分更稳妥。 |
| `classification` | `Text Classification` | 是 | 与 doccano 原生分类能力直接匹配，导入导出简单。 |
| `quality_judge` | `Text Classification` | 是 | 质量判断本质是有限标签判定，适配分类项目。 |
| `ner` / `span_extraction` | `Sequence Labeling` | 否（未来扩展） | 技术上适配，但不属于本轮最小闭环优先范围。 |
| `qa_dialogue` | 不建议纳入 doccano MVP | 否 | 多轮上下文与复杂流程更依赖灵活界面与流程编排，MVP 阶段成本高、收益低。 |

---

## 4. 不适合 doccano MVP 的任务

以下任务不纳入 doccano MVP，优先放在 Label Studio：

- **多轮复杂工作流**
  - 典型特征：多轮 history、阶段化判断、跨回合依赖。
  - 原因：doccano MVP 项目形态更偏单样本单任务，不适合流程型编排。

- **多字段联合裁决**
  - 典型特征：同条样本需同时产出主标签、冲突等级、裁决状态、规则引用。
  - 原因：doccano 可做基础标注，但联合流程与状态管理成本较高。

- **复杂 evidence workflow**
  - 典型特征：需要稳定维护证据片段、边界争议与复核流转。
  - 原因：MVP 阶段优先保证主标签与答案闭环，复杂证据流程更适合 Label Studio 的灵活配置。

**结论**：doccano 用于标准 NLP 最小任务闭环；Label Studio 承载复杂多字段、多阶段流程。

---

## 5. 推荐 MVP 项目拆分

### Project A — QA Answer (Seq2Seq)

- 目标：生成/抽取最终答案文本。
- 输入字段：
  - `question`
  - `context`
- 输出字段：
  - `final_answer`

### Project B — QA Support Classification

- 目标：对“答案是否被上下文直接支持”做统一标签判断。
- 输入字段：
  - `question`
  - `context`
  - `answer_candidate` / `reference`
- 标签集合（与 Day32 对齐）：
  - `SUPPORTED`
  - `UNSUPPORTED`
  - `MULTI_ANSWER`
  - `AMBIGUOUS_SPAN`

---

## 6. 最小字段结构

### 必需字段

- `sample_id`
- `task_type`
- `question`
- `context`

### 可选字段

- `reference`
- `answer_candidate`

### 暂缓字段

- `evidence_span`
- `rule_id`

说明：暂缓字段不在本轮 doccano MVP 强绑定，避免阻塞闭环；后续如需增强复核能力再引入。

---

## 7. 风险与缓解

- **风险：`sample_id` 丢失**
  - 影响：导出结果无法回写原样本，后处理断链。
  - 最小缓解动作：导入前检查 `sample_id` 存在；导出后抽样校验主键可追溯。

- **风险：label 漂移**
  - 影响：同一任务跨平台语义不一致，统计不可比。
  - 最小缓解动作：固定只允许 Day32 定义标签；项目配置中禁止临时新增同义标签。

- **风险：`task_type` 路由错误**
  - 影响：样本进入错误项目，造成标注失真。
  - 最小缓解动作：导入前做一次 `task_type -> project` 映射核对清单。

- **风险：`qa_span` 与单一 project type 不完全匹配**
  - 影响：单项目无法同时稳定承载答案与支持性判断。
  - 最小缓解动作：采用 A/B 双项目拆分；分别产出 `final_answer` 与支持性标签。

---

## 8. Definition of Done

满足以下条件即判定本任务完成：

- 能成功导入 doccano（按映射进入对应项目）。
- 能完成小批量样本标注（至少覆盖 `qa_span` 闭环）。
- 能导出 JSONL。
- 导出结果中 `sample_id` 未丢失。
- 导出结果可进入 pandas 后处理（可按 `sample_id` join 源样本）。
