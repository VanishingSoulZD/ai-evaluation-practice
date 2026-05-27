# Day34：doccano vs Label Studio 对比（AI 评测链路）

> 背景：Day33 已完成 Label Studio MVP，Day34 正在完成 doccano MVP。本文只讨论两者在当前评测链路中的工具定位与数据结构差异，不做泛化选型。

## 1. 两个平台定位

- **doccano**：偏传统 NLP 标注平台，强调“轻量、标准任务、快速上手”。
- **Label Studio**：偏通用 AI 数据标注平台，强调“可配置、可扩展、多任务形态”。

在本项目语境下，两者都属于**人工标注入口层**，不是最终评测器本身。

## 2. 适合任务

### doccano 更适合

- 文本分类（如支持/不支持判定）
- 序列标注（NER/关键词片段）
- 结构较固定的文本任务
- 目标是快速建立“可导出+可解析”的 NLP 基线

### Label Studio 更适合

- 需要同时展示多个字段并灵活排版的任务
- 任务规则会频繁迭代、需要反复改界面
- 后续可能扩展到多模态或复杂工作流的任务

## 3. UI 灵活性

- **doccano**：UI 路径短、操作直接，但可定制空间相对有限；更像“固定范式内高效率”。
- **Label Studio**：UI 可通过配置进行更细粒度控制；代价是学习/维护成本更高。

结论：如果当前阶段优先“尽快标起来”，doccano 的交互摩擦通常更低；如果优先“界面表达复杂任务语义”，Label Studio 更稳。

## 4. schema 灵活性

- **doccano**：项目类型驱动 schema，整体更规整、更固定。
- **Label Studio**：界面配置驱动 schema 映射，字段组织更自由。

工程含义：

- doccano 输出约束更强，脚本端更容易形成稳定解析模板；
- Label Studio 表达能力更强，但需要更明确的“配置版本管理 + 映射规则管理”。

## 5. 导出结构

在 MVP 阶段应重点看三件事：`sample_id` 是否保留、标签是否稳定、结构是否可批处理。

- **doccano**：导出结构通常更贴近标准 NLP 管道，字段层级相对直接。
- **Label Studio**：导出信息更丰富，但原始字段与标注结果可能分层更复杂，常需要二次展平。

## 6. pandas / scripts 兼容性

- **doccano**：
  - 更容易直接 `read_json/read_csv` 后进入聚合统计；
  - 适合快速写“标签分布、按任务类型切片”的脚本。
- **Label Studio**：
  - 同样可进入 pandas，但往往先做一层 schema normalize；
  - 适合在已有映射器后做复杂分析。

实操建议：统一中间层 schema（如 `sample_id/task_type/label/tool/config_version`），避免脚本绑定平台私有结构。



## 6.1 推荐统一 export schema（doccano MVP）

为保证 Day35/36 可直接进入一致性与冲突分析，建议先定义**平台无关的导出中间 schema**。

### 必须保留字段（最低集合）

- `sample_id`：样本唯一标识（来自 day31 原始样本）
- `task_type`：任务类型（如 `qa_span` / `qa_dialogue` / `classification`）
- `label`：本次人工主标签（单值）
- `annotator`：标注者标识（用户名或工号）
- `tool`：固定写入 `doccano` 或 `label_studio`
- `project_id`：平台内项目标识（便于回溯）
- `record_id`：平台内任务/数据行标识
- `annotation_id`：平台内标注结果标识
- `created_at` / `updated_at`：结果时间戳（UTC）
- `schema_version`：统一 schema 版本（如 `eval_export_v1`）
- `config_version`：标注配置版本（如 `day34_doccano_tc_v1`）

### 推荐 JSONL 示例（统一后的单行）

```json
{"sample_id":"day31_000123","task_type":"qa_span","label":"SUPPORTED","annotator":"u_alice","tool":"doccano","project_id":12,"record_id":3456,"annotation_id":7890,"created_at":"2026-05-27T10:20:31Z","updated_at":"2026-05-27T10:21:08Z","schema_version":"eval_export_v1","config_version":"day34_doccano_tc_v1"}
```

说明：上例是**normalize 后的目标格式**，不是要求平台原生导出完全同构。

## 6.2 sample_id 与 label 保留策略

### sample_id 保留策略

1. 导入 doccano 前，确保 `sample_id` 已在源数据中稳定存在；
2. 导出后若出现字段层级变化，normalize 时必须把 `sample_id` 提升到顶层；
3. 禁止在清洗阶段重写 `sample_id`（只允许 trim/类型标准化）；
4. 若出现缺失 `sample_id`，该条记录标记为 `invalid_record`，不得进入 metrics。

### label 保存策略

1. 统一主标签字段名为 `label`（跨平台一致）；
2. 多标签任务需拆分：
   - `label` 存主判定；
   - 可选 `label_secondary` / `label_list` 存补充；
3. 空标签记录不删除，保留并标记 `label_status="empty"`，用于统计漏标率；
4. Label Studio 的控件名（如 `annotation_label`）在 normalize 后映射为统一 `label`。

## 6.3 normalize 层建议（pandas/read_json 兼容）

建议把平台导出接入两段式处理：

1. **raw loader**：只负责读取平台原始 JSON/JSONL/CSV；
2. **normalizer**：只负责字段映射、类型收敛、主键生成与校验。

### pandas 兼容建议

- JSONL 优先使用：`pd.read_json(path, lines=True)`；
- 对嵌套结构使用 `json_normalize` 或显式展开函数，避免“隐式列爆炸”；
- 时间字段统一转 UTC 字符串（ISO-8601）；
- 主键字段统一转 string，避免 int/str 混用导致 join 失败。

### normalize 输出校验（最小）

- 主键唯一性：`(sample_id, annotator, round_id)` 不重复；
- 必填完整性：`sample_id/task_type/label/tool/schema_version` 非空；
- 标签合法性：`label` 必须在当轮标签集合内。

## 6.4 与 Label Studio export 的结构差异（工程视角）

| 对比点 | doccano 常见形态 | Label Studio 常见形态 | normalize 动作 |
|---|---|---|---|
| 主体结构 | 偏平铺或轻嵌套 | 常见深层嵌套（任务/结果/控件） | 展平并映射统一字段 |
| 标签位置 | 相对集中 | 可能位于 result 列表内 | 提取主标签到 `label` |
| 元信息保留 | 项目/记录字段较直接 | 任务 data 与标注 result 分离 | 合并 data + result |
| 解析成本 | 中低 | 中高 | 统一走 normalizer |

结论：两者都可进入同一评测脚本，但 Label Studio 通常需要更显式的展平规则。

## 6.5 schema 风险与版本管理

### 主要风险

1. 平台升级导致导出字段路径变化；
2. 标注配置调整导致标签集合变化；
3. 多人标注时主键设计不足，造成覆盖或重复统计。

### 版本管理约定（MVP）

- `schema_version`：仅描述“统一导出中间层”结构版本；
- `config_version`：描述当轮标注标签/界面配置版本；
- `tool_version`：可选记录平台版本，便于回放兼容问题。

### 多标注者主键建议

在 Day35/36 引入双人标注后，建议主键采用：

- 业务主键：`(sample_id, annotator, round_id)`
- 技术追溯键：`(tool, project_id, record_id, annotation_id)`

其中：

- `round_id` 用于区分复标轮次（如 `r1`/`r2`）；
- 业务主键用于一致性统计；
- 技术追溯键用于回查平台原始记录。


## 7. MVP 推荐场景

### 推荐 doccano 的场景

1. 目标是本周内快速跑通第二套标注闭环；
2. 当前任务以文本分类/序列标注为主；
3. 团队希望先降低操作复杂度，再逐步加流程治理。

### 推荐 Label Studio 的场景

1. 任务字段多、展示逻辑复杂；
2. 后续要做更复杂 UI/流程编排；
3. 需要在同一平台承载更多任务形态。

## 8. 不推荐场景

### doccano 不推荐

- 需要高度自定义标注界面与复杂组件组合；
- 任务输入结构变化频繁，且需要细粒度动态展示策略。

### Label Studio 不推荐（在当前 MVP 阶段）

- 仅做标准文本分类且时间紧、希望最短路径交付；
- 团队尚未准备好维护较复杂的配置与映射。

## 9. AI 评测链路中的位置

两者在链路中的角色一致：

```text
统一样本
  -> 标注平台（doccano / Label Studio）
  -> 人工标注结果导出
  -> 统一 schema 转换
  -> pandas / 统计脚本
  -> 一致性分析与评测指标
```

关键不是“选唯一平台”，而是：

1. 标注规范一致；
2. 导出字段可回溯（尤其 sample_id）；
3. 跨平台结果可归一到同一分析脚本。

## 10. 对比总表（MVP 结论）

| 维度 | doccano | Label Studio | 当前结论（Day34） |
|---|---|---|---|
| 平台定位 | 传统 NLP 标注 | 通用 AI 标注平台 | 都是“标注入口层” |
| 适合任务 | 分类、序列标注、结构固定文本 | 多字段复杂任务、可扩展任务形态 | 按任务复杂度选择 |
| UI 灵活性 | 中等，偏固定流程 | 高，可配置能力强 | 灵活性越高，维护成本越高 |
| Schema 灵活性 | 中等偏低，项目类型约束明显 | 高，配置驱动字段映射 | doccano 更稳，LS 更灵活 |
| 导出结构 | 相对规整，便于 NLP 脚本消费 | 信息丰富但常需二次展平 | 都可用，LS 需更强映射治理 |
| pandas 兼容性 | 直接性更好 | 依赖 normalize 层 | 建议统一中间 schema |
| MVP 推荐 | 快速跑通标准 NLP 闭环 | 复杂任务表达与后续扩展 | Day34 优先 doccano，保留 LS 作为复杂任务平台 |

## 11. 明确 MVP 推荐方案

**当前推荐：双平台并存，但分工明确。**

- **Day34~Day35 的主路径**：以 doccano 作为标准文本任务的快速执行平台。
- **复杂任务或后续扩展路径**：保留 Label Studio 作为高灵活度平台。
- **脚本侧统一策略**：不让分析脚本直接绑定某一平台导出；统一先过 normalize 层。

这能同时满足“短期交付速度”和“中期扩展空间”。

## 12. 当前 MVP 限制

1. 结论基于 Day33/Day34 的最小闭环，不代表生产环境全量能力对比；
2. 尚未引入双标仲裁与一致性统计（如 Kappa）结果作为量化依据；
3. 尚未完成大规模样本压测，当前结论偏工程可用性而非性能上限；
4. 导出后统一 schema 仍需在 Day35 继续固化。
