# Day35 Task 3 — Disagreement 分类体系（MVP）

> 适用范围：Iteration 035 双人标注分歧分析。  
> 目标：提供可直接落地到 CSV 与后续统计的最小可运行 taxonomy。  
> 非目标：不改 Day32 标签体系、不引入复杂 ontology、不做脚本实现。

---

## 1. 设计原则（MVP）

1. **单一主分类**：每条分歧样本仅允许 1 个 `disagreement_type`（不做多标签）。
2. **分层建模**：
   - `disagreement_type` = 现象层（分歧“是什么”）
   - `root_cause` = 因果层（分歧“为什么”）
   - `action` = 闭环层（下一步“做什么”）
3. **可统计优先**：核心字段采用 enum，避免自由文本主导。
4. **先可判后细化**：先保证稳定归类，再逐步补充示例与规则文字。

---

## 2. `disagreement_type`（顶层分类）

> 顶层分类必须且仅能使用以下四类。

| enum | 含义（ intended meaning ） | 适用边界（boundary condition） |
|---|---|---|
| `LABEL_AMBIGUITY` | 标签语义、答案粒度或证据边界定义不够稳定，导致不同标注员都“看起来合理”但标签不一致 | 样本信息基本足够、规则也无明显冲突；分歧主要来自标签/输出边界解释 |
| `GUIDELINE_INTERPRETATION_BIAS` | 对同一规则文本或规则优先级理解不同，导致执行口径分叉 | 样本可判，但分歧关键在“规则怎么用”而非“信息是否够” |
| `INSUFFICIENT_INFORMATION` | 样本本身信息不足、截断、噪声或关键证据缺失，无法稳定映射唯一标签 | 先验优先级最高；一旦成立，不再归入其他类别 |
| `BOUNDARY_CASE` | 合法但压边的困难样本，在现有规则下存在多个近似合理判法 | 最后兜底类；仅在前三类均不成立时使用 |

---

## 3. 分类优先级规则（必须执行）

分类顺序固定为：

1. `INSUFFICIENT_INFORMATION`
2. `GUIDELINE_INTERPRETATION_BIAS`
3. `LABEL_AMBIGUITY`
4. `BOUNDARY_CASE`

### 3.1 该顺序的原因

- **信息不足优先于边界争议**：若关键证据缺失，分歧本质是“不可判”而不是“边界难判”。
- **规则冲突先于标签歧义**：若分歧由规则优先级/解释冲突触发，应先归因到规范层，而不是标签定义层。
- **`BOUNDARY_CASE` 是最后兜底**：避免把所有难例都扔进边界类，导致 taxonomy 失去诊断价值。

### 3.2 最小判定流程（决策树）

- Q1：样本是否缺关键证据、存在截断/噪声致核心不可判？
  - 是 → `INSUFFICIENT_INFORMATION`
  - 否 → Q2
- Q2：分歧是否主要来自规则解释或规则优先级冲突？
  - 是 → `GUIDELINE_INTERPRETATION_BIAS`
  - 否 → Q3
- Q3：分歧是否主要来自标签语义、span 粒度或输出规范边界？
  - 是 → `LABEL_AMBIGUITY`
  - 否 → `BOUNDARY_CASE`

---

## 4. `root_cause`（根因分类）

> `root_cause` 是因果层，不等于 `disagreement_type`。  
> 一条记录建议 1 个主根因（可选 secondary 字段做补充）。

| enum | 定义 | 常见对应 `disagreement_type` |
|---|---|---|
| `MISSING_EVIDENCE` | 样本中缺少判定所需关键事实 | `INSUFFICIENT_INFORMATION` |
| `CONFLICTING_EVIDENCE` | 样本内证据互相冲突，或 reference/context 明显不一致 | `INSUFFICIENT_INFORMATION`, `BOUNDARY_CASE` |
| `SPAN_GRANULARITY` | 证据跨度切分、答案粒度边界不一致 | `LABEL_AMBIGUITY` |
| `OUTPUT_NORMALIZATION` | 输出规范化口径不一致（冠词、大小写、格式） | `LABEL_AMBIGUITY` |
| `RULE_PRIORITY_CONFLICT` | 规则层级或适用优先级理解不同 | `GUIDELINE_INTERPRETATION_BIAS` |
| `RULE_TEXT_UNDERSPECIFIED` | 规则描述不够具体，存在多解空间 | `GUIDELINE_INTERPRETATION_BIAS`, `BOUNDARY_CASE` |
| `TASK_SCHEMA_GAP` | 任务 schema/label_map/字段定义不完整或不一致 | `GUIDELINE_INTERPRETATION_BIAS`, `INSUFFICIENT_INFORMATION` |
| `ANNOTATOR_OVERRULE_BY_HEURISTIC` | 标注员以经验/常识覆盖明文规则 | `GUIDELINE_INTERPRETATION_BIAS` |

### 4.1 与 `disagreement_type` 的关系

- `disagreement_type`：用于分歧分桶统计（例如“哪类分歧最多”）。
- `root_cause`：用于返工定位（例如“该补规则、补示例还是查数据质量”）。
- 同一 `disagreement_type` 可对应多个可能根因，但 MVP 建议每条仅记录一个主根因，保证统计稳定。

---

## 5. `action`（闭环动作）

> `action` 用于裁决后反馈闭环；必须可聚合统计，不应自由文本优先。

| enum | 动作定义 | 典型触发 |
|---|---|---|
| `ADJUDICATE_ONLY` | 仅完成当前样本裁决，不做规则或示例更新 | 一次性个例，复现概率低 |
| `ADD_EXAMPLE` | 增补正/反/边界示例到示例库 | 高频误判、规则已足够但缺直观样例 |
| `CLARIFY_RULE_TEXT` | 澄清现有规则文本，不改标签体系 | 规则描述含混、术语歧义 |
| `ADD_DECISION_TREE_STEP` | 在执行流程增加显式判定步骤 | 标注流程缺少“先判可判性”等关键门槛 |
| `STANDARDIZE_OUTPUT_FORMAT` | 补充输出标准化规范（span、格式、规范化） | `dog` vs `the dog`、span 切分不一致 |
| `DATA_QUALITY_FLAG` | 标记并追踪数据质量问题 | 截断、脏数据、字段缺失 |
| `ESCALATE_SCHEMA_CHANGE` | 升级到后续迭代做 schema/标签结构调整 | 超出当前 MVP 能力边界 |

### 5.1 设计要求

- `action` 应支持后续统计（例如各动作占比、动作与 root_cause 关联）。
- 可增加 `action_note`（可选）做一句话补充，但主动作必须是 enum。

---

## 6. 分类边界规则（防止混淆）

### 6.1 `INSUFFICIENT_INFORMATION` vs `BOUNDARY_CASE`

- 前者：**缺信息导致不可稳定判定**（不可判）。
- 后者：**信息在场但压边**（可判但口径容易分叉）。

### 6.2 `GUIDELINE_INTERPRETATION_BIAS` vs `LABEL_AMBIGUITY`

- 前者：核心冲突在“规则如何解释/优先级如何应用”。
- 后者：核心冲突在“标签或输出边界如何落地”。

### 6.3 `LABEL_AMBIGUITY` vs `BOUNDARY_CASE`

- 前者：可通过明确粒度、span 规则、标准化约束迅速收敛。
- 后者：即使规则清晰仍接近决策边界，通常需要沉淀边界样例。

### 6.4 禁止事项（MVP）

- 不允许新增第 5 个顶层 `disagreement_type`。
- 不允许同一记录打多个 `disagreement_type`。
- 不允许以自由文本替代 enum 主字段。

---

## 7. 最小示例（每类 1–2 个）

> 示例与 Day32 语义保持一致，聚焦 QA / span / normalization。

### 7.1 `LABEL_AMBIGUITY`

- **LA-01（答案粒度）**
  - Context: “Solar power is the conversion of energy from sunlight into electricity.”
  - Q: “What does solar power convert into electricity?”
  - A 标注：`sunlight`
  - B 标注：`energy from sunlight`
  - 判定：`LABEL_AMBIGUITY`
  - root_cause: `SPAN_GRANULARITY`
  - action: `STANDARDIZE_OUTPUT_FORMAT`

- **LA-02（输出标准化）**
  - Context: “He threw a red ball, and the dog ran after it.”
  - Q: “Who ran after the ball?”
  - A 标注：`dog`
  - B 标注：`the dog`
  - 判定：`LABEL_AMBIGUITY`
  - root_cause: `OUTPUT_NORMALIZATION`
  - action: `STANDARDIZE_OUTPUT_FORMAT`

### 7.2 `GUIDELINE_INTERPRETATION_BIAS`

- **GI-01（外部知识外推）**
  - Context: “The company is headquartered in Munich.”
  - Q: “Which country is the HQ in?”
  - A 按“禁止外推”标 `UNSUPPORTED`
  - B 用常识映射 Munich→Germany 标 `SUPPORTED`
  - 判定：`GUIDELINE_INTERPRETATION_BIAS`
  - root_cause: `ANNOTATOR_OVERRULE_BY_HEURISTIC`
  - action: `CLARIFY_RULE_TEXT`

- **GI-02（规则优先级理解差异）**
  - 同一样本中，A 先执行“先判可判性”进入待裁决；B 直接按候选答案给主标签。
  - 判定：`GUIDELINE_INTERPRETATION_BIAS`
  - root_cause: `RULE_PRIORITY_CONFLICT`
  - action: `ADD_DECISION_TREE_STEP`

### 7.3 `INSUFFICIENT_INFORMATION`

- **II-01（关键事实缺失）**
  - Context: “The author graduated from PKU and works at an institute.”
  - Q: “What year was the author born?”
  - A/B 分别猜测不同年份
  - 判定：`INSUFFICIENT_INFORMATION`
  - root_cause: `MISSING_EVIDENCE`
  - action: `ADJUDICATE_ONLY`

- **II-02（截断风险）**
  - reference 显示应可回答，但当前 context 片段不含关键句。
  - 判定：`INSUFFICIENT_INFORMATION`
  - root_cause: `CONFLICTING_EVIDENCE`
  - action: `DATA_QUALITY_FLAG`

### 7.4 `BOUNDARY_CASE`

- **BC-01（多答案边界）**
  - Context: “The project is co-led by Zhang San and Li Si.”
  - Q: “Who is the project lead?”
  - A 选张三，B 选李四
  - 判定：`BOUNDARY_CASE`
  - root_cause: `RULE_TEXT_UNDERSPECIFIED`
  - action: `ADD_EXAMPLE`

- **BC-02（span 切分并列边界）**
  - 答案可确定，但两个最小充分 span 都可复现标签，现规则未规定优先切法。
  - 判定：`BOUNDARY_CASE`
  - root_cause: `RULE_TEXT_UNDERSPECIFIED`
  - action: `ADD_EXAMPLE`

---

## 8. 推荐 CSV Schema（紧凑版）

### 8.1 字段定义

| field | required | type | 说明 |
|---|---:|---|---|
| `sample_id` | Y | string | 样本唯一 ID |
| `task_type` | Y | string | 任务类型（如 qa_span / qa_dialogue） |
| `annotator_a_label` | Y | string | 标注员 A 主标签 |
| `annotator_b_label` | Y | string | 标注员 B 主标签 |
| `disagreement_type` | Y | enum | 四选一：`LABEL_AMBIGUITY` / `GUIDELINE_INTERPRETATION_BIAS` / `INSUFFICIENT_INFORMATION` / `BOUNDARY_CASE` |
| `root_cause` | Y | enum | 根因主类（见第 4 节） |
| `action` | Y | enum | 闭环动作（见第 5 节） |
| `final_decision_label` | Y | string | 裁决后最终标签 |
| `rule_id_a` | O | string | A 引用规则 ID |
| `rule_id_b` | O | string | B 引用规则 ID |
| `severity` | O | enum | `P1` / `P2` / `P3` |
| `needs_guideline_update` | Y | enum | `yes` / `no` |
| `adjudicator_note` | O | string | 一句话裁决说明（建议 ≤ 200 chars） |

> O = Optional, Y = Required。

### 8.2 分析友好性说明

- Required 字段足以支撑最小统计：
  - 分歧分布（按 `disagreement_type`）
  - 返工优先级（按 `root_cause` × `action`）
  - 裁决结果稳定性（按 `final_decision_label`）
- Optional 字段用于审计追溯，不阻塞主流程。

---

## 9. 风险与反模式

### 9.1 主要风险

1. **把 `BOUNDARY_CASE` 当垃圾桶**：导致问题无法定向改进。
2. **`disagreement_type` 与 `root_cause` 混填**：统计口径失真。
3. **过早引入多标签分类**：一致性显著下降，裁决成本飙升。
4. **action 自由文本化**：无法做聚合与优先级排序。
5. **示例与主规范漂移**：示例说法与 guideline 优先级冲突。

### 9.2 反模式（应避免）

- “看起来复杂就归 `BOUNDARY_CASE`”。
- “先写大段 note，最后补一个随意 enum”。
- “根因不确定就新增根因枚举”。
- “因为个例而升级 schema”。

---

## 10. 下游兼容性说明（Day36 准备）

本 taxonomy 对下游一致性分析的直接支持：

1. **一致性诊断分层**：可区分数据问题、规则问题、标签边界问题。
2. **裁决负担评估**：可统计哪些分歧类型最依赖人工裁决。
3. **规范返工优先级**：
   - 高频 `RULE_TEXT_UNDERSPECIFIED` → 优先补规则文本
   - 高频 `OUTPUT_NORMALIZATION` → 优先补输出规范
   - 高频 `MISSING_EVIDENCE` → 优先数据质量治理
4. **Kappa 前置清洗准备**：先减少“非语义分歧”，再做一致性指标更可信。

---

## 11. 最小执行建议（本轮）

1. 先在分歧样本上强制执行第 3 节分类顺序。
2. 每条记录只填一个 `disagreement_type` 与一个 `root_cause`。
3. `action` 必填且必须是 enum，不允许空。
4. 每批次复盘：输出 `disagreement_type`/`root_cause`/`action` 三个 Top-3。

---

## 12. 变更控制（MVP）

- 本文档是 Day35 MVP 版 taxonomy 规范。
- 后续如需扩展枚举，应满足：
  1) 连续两批次出现无法归类样本；
  2) 现有 enum 的误分类率可被证明偏高；
  3) 扩展后仍可保持聚合统计稳定。

