# Day 33：Label Studio 最小安装与启动说明

## 1. Label Studio 简介（简短）

Label Studio 是一个通用的数据标注工具，支持文本、图像、音频等多种任务类型。对本项目来说，先用它完成“安装 → 启动 → 登录 → 创建项目”的最小闭环即可，不涉及生产部署。

---

## 2. 使用 `uv` 的安装方式

> 前提：你本机已安装 `uv`（可用 `uv --version` 验证）。

在项目根目录执行：

```bash
# 进入仓库根目录
cd /workspace/ai-evaluation-practice

# 创建并使用本地虚拟环境（目录名为 .venv）
uv venv

# 在虚拟环境中安装 Label Studio
uv pip install label-studio
```

可选验证：

```bash
uv run label-studio --version
```

---

## 3. 启动命令

在项目根目录执行：

```bash
cd /workspace/ai-evaluation-practice
uv run label-studio start
```

如果你希望显式指定监听端口（例如 8080）：

```bash
cd /workspace/ai-evaluation-practice
uv run label-studio start --port 8080
```

---

## 4. 默认访问地址

服务启动后，默认在浏览器访问：

- `http://localhost:8080`

如果你通过 `--port` 指定了其他端口，请把地址中的 `8080` 替换为对应端口。

---

## 5. 首次创建账号流程

首次打开页面时，按界面引导完成初始化：

1. 进入 `http://localhost:8080`；
2. 点击 **Sign up**（或初始化注册入口）；
3. 输入邮箱、用户名和密码；
4. 提交后自动登录（或跳转登录页后再登录）；
5. 登录成功后可创建第一个标注项目。

> 说明：首次创建的账号通常就是当前本地实例的管理员账号。

---

## 6. 数据导入说明（MVP）

### 6.1 推荐导入格式（JSONL vs CSV）

**结论：本轮推荐优先用 JSONL 导入。**

- JSONL 更适合保留结构化字段（如 `history` 的 JSON 数组字符串），字段语义更直观；
- CSV 也可导入，但在引号、逗号、换行和 JSON 字符串转义上更容易踩坑；
- 本轮只做 MVP，不做复杂 schema 转换，因此直接使用 `data/day31_samples.jsonl` 最稳妥。

可选场景：如果你只做快速浏览或与表格工具联动，CSV 仍可作为备选。

### 6.2 day31 样本字段说明

基于 `day31` 样本前几条记录，当前 schema 包含以下字段：

- `sample_id`：样本唯一 ID（建议在导出后用于回溯）；
- `source_dataset`：来源数据集（如 `squad`、`coqa`）；
- `subtask`：子任务标识（当前示例中可为空字符串）；
- `task_type`：任务类型（如 `qa_span`、`qa_dialogue`）；
- `difficulty_tag`：难度标签（如 `easy`、`medium`）；
- `input`：主输入文本（通常可作为标注时的主要阅读字段）；
- `context`：上下文文本；
- `question`：问题文本；
- `history`：多轮历史（字符串形式，内容通常是 JSON 数组）；
- `reference`：参考答案（用于质检或比对，不一定直接参与盲标）；
- `label`：预留标签字段（当前样本多数为空）；
- `split`：数据划分（如 `dev`、`check`、`annotation`）。

### 6.3 Label Studio 中的字段映射

建议采用“文本阅读 + 结果标签”最小配置，映射如下：

- 主展示区：
  - `input`（必显，给标注员快速理解任务）；
  - `context`（建议显示）；
  - `question`（问答类任务建议显示）；
- 辅助信息区：
  - `history`（多轮任务显示；单轮任务可留空展示）；
  - `reference`（如做盲标可先不显示给标注员）；
- 元信息（不需要单独做控件，但应保留在任务数据中）：
  - `sample_id`, `source_dataset`, `task_type`, `difficulty_tag`, `split`, `subtask`。

MVP 原则：先保证“能看到输入并完成标注”，不在本轮引入复杂动态模板或 schema 重写。

### 6.4 导入流程

1. 在 Label Studio 创建文本项目（例如：`iter033-day31-mvp`）。
2. 打开 **Import** 页面。
3. 选择 `data/day31_samples.jsonl`（推荐）上传。
4. 若使用 CSV，则选择 `data/day31_samples.csv`，并确认首行为表头。
5. 导入后先抽查前 5~10 条任务，确认字段显示正常。
6. 再进入标注页面开始人工标注。

### 6.5 导入后的检查项

至少检查以下 6 项：

1. **任务数是否正确**：导入总数与源文件行数预期一致；
2. **字段是否齐全**：`input/context/question/history/reference` 至少能在数据中取到；
3. **中文与特殊字符**：无乱码、无截断；
4. **`history` 可读性**：多轮样本的历史字段不是损坏字符串；
5. **空字段可接受**：如 `subtask`、`label` 为空时不影响加载；
6. **样本可回溯**：任务中能定位 `sample_id`。

### 6.6 常见导入错误

1. **JSON 解析失败 / JSONL 非逐行 JSON**  
   - 原因：文件不是一行一个 JSON 对象，或存在非法逗号/引号。  
   - 处理：确保 `.jsonl` 每行是完整 JSON。

2. **CSV 列错位**  
   - 原因：文本内逗号、引号未正确转义。  
   - 处理：优先改用 JSONL；若坚持 CSV，先用工具重新导出规范 CSV。

3. **字段名不匹配**  
   - 原因：配置中引用了不存在字段（例如写成 `contexts` 而不是 `context`）。  
   - 处理：按 day31 实际字段名逐一核对。

4. **导入后看不到关键信息**  
   - 原因：标注界面未绑定对应字段（例如没显示 `question`）。  
   - 处理：回到 Labeling Interface 增加对应文本展示控件并重新保存。

---

## 7. 如何停止服务

在运行 `uv run label-studio start` 的终端窗口中：

- 按 `Ctrl + C` 即可停止服务。

如果是后台运行（不推荐本次最小流程使用），可通过进程管理方式结束对应进程。

---

## 8. 常见启动问题（至少 2 个）

### 问题 1：`uv: command not found`

**现象**：终端提示找不到 `uv`。  
**原因**：本机尚未安装 `uv`，或 PATH 未生效。  
**处理**：先安装 `uv` 并重新打开终端，再执行 `uv --version` 验证。

### 问题 2：端口被占用（例如 `Address already in use`）

**现象**：启动时报端口冲突。  
**原因**：`8080` 已被其他程序占用。  
**处理**：改用其他端口启动，例如：

```bash
uv run label-studio start --port 8081
```

然后访问 `http://localhost:8081`。

### 问题 3：依赖安装失败或网络超时

**现象**：`uv pip install label-studio` 失败。  
**原因**：网络不稳定，或 Python/构建环境异常。  
**处理**：

1. 先检查 Python 版本与 `uv` 是否可用；
2. 重新执行安装命令；
3. 必要时切换到网络更稳定的环境后重试。

---

## 9. 最小可复制命令清单

```bash
cd /workspace/ai-evaluation-practice
uv venv
uv pip install label-studio
uv run label-studio --version
uv run label-studio start
```

---

## 10. Day33 MVP 标注界面配置落地（Task 3）

本节给出可直接导入 Label Studio 的 **单文件 XML** MVP 配置，目标是先跑通 Day33 标注闭环，不引入多项目、多页面或复杂路由。

### 10.1 配置文件位置

- `configs/labelstudio/day33_mvp_label_config.xml`

### 10.2 如何导入 XML 配置

1. 启动 Label Studio：
   - `uv run label-studio start`
2. 创建或打开 Day33 项目（建议单项目，例如 `iter033-day33-mvp`）。
3. 进入项目设置中的 **Labeling Interface**。
4. 选择代码/XML 编辑模式。
5. 将 `configs/labelstudio/day33_mvp_label_config.xml` 内容粘贴并保存。
6. 回到 Data Import，导入 `data/day31_samples.jsonl`。
7. 打开任务检查字段和标签是否正常显示。

> 本 MVP 采用单页面统一模板，不创建多 XML，不做任务路由。

### 10.3 字段展示说明（与 day31 schema 对齐）

界面展示字段如下（按顺序）：

1. `context`：主判定文本，所有 span 标注统一绑定该字段。
2. `question`：问题文本，用于问答判定。
3. `reference`：参考答案，MVP 阶段允许直接显示。
4. `history`：对话历史，按字符串原样显示，不做 prettify。

同时展示元信息：

- `sample_id`
- `task_type`
- `source_dataset`
- `difficulty_tag`
- `split`

### 10.4 标签用途说明

主标签控件：`annotation_label`（单选）

- `SUPPORTED`：答案被上下文直接支持。
- `UNSUPPORTED`：答案不被上下文支持或冲突。
- `MULTI_ANSWER`：存在多个可支持答案且无法唯一化。
- `AMBIGUOUS_SPAN`：答案可支持，但证据边界难以唯一。
- `DIALOGUE_GOOD`：对话类回复质量可接受。
- `DIALOGUE_BAD`：对话类回复质量不可接受。
- `CLASS_A`：分类任务占位标签 A（MVP）。
- `CLASS_B`：分类任务占位标签 B（MVP）。
- `NEED_REVIEW`：信息不足或规则冲突，需复核。

### 10.5 task_type 与标签映射（MVP 口径）

- `qa_span`：
  - 首选：`SUPPORTED / UNSUPPORTED / MULTI_ANSWER / AMBIGUOUS_SPAN`
  - 必要时：`NEED_REVIEW`
- `qa_dialogue`：
  - 首选：`DIALOGUE_GOOD / DIALOGUE_BAD`
  - 必要时：`NEED_REVIEW`
- `classification`：
  - 暂用：`CLASS_A / CLASS_B`
  - 必要时：`NEED_REVIEW`

### 10.6 Evidence span 使用说明

- 控件名：`evidence_label`
- 标签值：`EVIDENCE`
- 绑定目标：`toName="context"`

使用规则：

1. 仅在 `qa_span` 任务中要求标注 evidence span。
2. span 应尽量满足“最小充分证据”。
3. `UNSUPPORTED` 场景可不标 span。
4. 若证据边界争议明显，可使用 `AMBIGUOUS_SPAN` 并在 `rationale` 记录原因。

### 10.7 final_answer 与 rationale 填写要求

- `final_answer`：
  - 填最终答案文本；
  - 若不可支持可填 `N/A`。

- `rationale`（必须保留）：
  - 填规则编号 + 简短理由（例如：`RC-8.1-R3: no direct evidence in context`）；
  - 用于后续 disagreement analysis、adjudication、failure analysis。

### 10.8 为什么采用当前 MVP 方案

1. 符合 Day33 目标：先跑通“导入 → 标注 → 导出”闭环。
2. 单 XML、单页面，降低配置复杂度与维护成本。
3. 用 `annotation_label` 避免与数据字段 `label` 混淆。
4. 统一将 span 绑定 `context`，便于后续一致性复核。
5. 兼容 `qa_span / qa_dialogue / classification` 三类任务，避免过早工程化拆分。

### 10.9 已知限制（MVP）

1. 未对不同 `task_type` 做动态隐藏/显示控件。
2. `classification` 仅使用占位标签 `CLASS_A/CLASS_B`。
3. `history` 原样字符串展示，可读性一般。
4. `reference` 默认可见，可能对盲标产生影响（后续可在流程层面约束）。
5. 未引入自动校验逻辑（如强制特定任务必须标 span）。


## 11. 人工标注 SOP（单人 MVP）

> 目标：在一个人执行的 MVP 场景下，确保“开始标注 → 处理歧义 → 导出结果”可重复、可追溯，并与 Day32 规则一致。

### 11.1 如何开始标注

1. 打开 Day33 项目（建议：`iter033-day33-mvp`）。
2. 进入 **Label** / **Start Labeling** 页面，按任务列表顺序开始。
3. 每条样本先做“可判性判断”：
   - 信息充足：进入正常打标；
   - 信息不足或冲突：转入“待裁决”流程（见 11.4、11.5）。
4. 保持固定节奏：逐条完成，不跳规则，不凭经验扩展标签。

对应 Day32 原则：先判可判性、原文优先、可复现。

### 11.2 如何查看输入字段

在单条任务页面按以下顺序阅读，减少漏看：

1. **元信息**：`sample_id`、`task_type`、`source_dataset`、`difficulty_tag`、`split`。
2. **主判定字段**：`context`（核心证据来源）。
3. **问题字段**：`question`（明确要回答的目标）。
4. **辅助字段**：`reference`、`history`（仅辅助理解，不可替代 `context` 证据）。

阅读顺序建议：`question -> context -> reference/history`，避免先入为主。

### 11.3 如何选择标签

基于 Day32 的问答抽取标签定义，按“四选一”执行：

1. `SUPPORTED`：`context` 中可直接定位证据支持答案。
2. `UNSUPPORTED`：缺证据、与原文冲突，或需要外部知识才能成立。
3. `MULTI_ANSWER`：存在多个同时成立且无法唯一化的答案。
4. `AMBIGUOUS_SPAN`：答案可确定，但最小充分证据跨度边界无法唯一。

推荐决策顺序：

1. 先排除 `UNSUPPORTED`（是否缺失/冲突/外推）。
2. 再判断是否 `MULTI_ANSWER`（是否多解且不可归并）。
3. 若单解可支持，检查是否为 `AMBIGUOUS_SPAN`。
4. 否则标 `SUPPORTED`，并保证证据可复核。

### 11.4 如何处理歧义样本

当出现以下任一情况，视为歧义样本：

- 关键信息缺失，无法唯一映射标签；
- 多标签证据强度相当；
- 输入截断/噪声影响核心判断。

处理步骤：

1. 当前样本不强行打主标签。
2. 标记“待裁决”（可通过备注、自定义标记或外部清单记录）。
3. 写清冲突点：字段位置 + 候选标签 + 触发规则编号。
4. 保存后继续下一条，避免在单条上长时间卡住。

### 11.5 如何记录待裁决样本

建议在项目内外维护一个最小记录表（CSV/Markdown 均可），字段至少包括：

- `sample_id`
- `task_type`
- `ambiguity_type`
- `candidate_labels`
- `evidence_span`
- `checked_rules`

单人 MVP 的执行要求：

1. 每次标注会话结束前，清点新增待裁决条目数。
2. 对待裁决样本按 P1/P2/P3 做简易优先级标记（可选）。
3. 二次回看时仅依据既有规则做裁决，不临时发明新标签。

### 11.6 如何避免误标

可直接执行以下“防误标清单”：

1. **只用样本内证据**：禁止用常识补全。
2. **先看 `question` 再看 `context`**：防止断章取义。
3. **每条仅选一个主标签**：不叠加互斥标签。
4. **高风险样本二次自检**：
   - 含否定词（如“不是/未/无”）；
   - 含时间、数量、比较级；
   - 含并列实体（易触发 `MULTI_ANSWER`）。
5. **抽样回放**：每完成 20~30 条，回看最近 5 条，检查口径漂移。
6. **歧义不上强结论**：无法稳定判断时进入待裁决，不为“完成率”硬判。

### 11.7 如何导出结果

完成一轮标注后执行：

1. 进入项目 **Export**。
2. 选择 JSON（优先）或 CSV 导出。
3. 导出后立即做 3 项检查：
   - 是否包含任务标识（如 `sample_id`）；
   - 是否包含标注结果字段（主标签、必要备注/证据）；
   - 待裁决样本是否可区分、可追踪。
4. 将导出文件保存到约定目录：
   - `outputs/day33_label_studio_export.*`
5. 记录本次导出时间、样本数、待裁决数，便于后续复盘。

---

以上 SOP 可直接支持 Day33 单人 MVP：先跑通一致性流程，再在后续迭代扩展双人复核与一致性统计。

---

## 12. 阶段总结与问题记录（Iteration 033 / Task 6）

### 12.1 Label Studio 的优势

结合 Day33 已完成内容（安装说明、数据导入、Label config、人工标注流程、导出结果说明），当前可确认的优势：

1. **闭环启动快**：本地可快速完成“导入样本→配置界面→人工标注→导出”的最小闭环。
2. **配置灵活**：可按任务字段自由组织展示区与标签控件，适配 `context/question/history/reference` 等多字段输入。
3. **元信息可保留**：`sample_id/task_type/source_dataset` 等字段可随任务保留，利于后续回溯与评测分析。
4. **适合作为基线平台**：在 AI 评测工程实践里，适合作为“先跑通流程、再做平台对比”的第一站。

### 12.2 当前 MVP 的局限

当前实现仍属于“最小可用”：

1. **单模板思路偏强**：对多任务混合场景的动态路由和分项目策略尚未展开。
2. **多轮信息可读性一般**：`history` 主要按字符串展示，标注员理解成本仍偏高。
3. **流程治理不足**：双标、仲裁、一致性统计（如 Kappa）尚未纳入 Day33 MVP。
4. **导出后标准化不足**：虽然能导出，但跨任务统一解析与直接对接评测脚本仍需二次整理。

### 12.3 哪些任务适合 Label Studio

在当前项目语境下，更适合以下任务：

1. **需要展示多个上下文字段的文本判定任务**（如 QA 证据支持性判断）。
2. **需要频繁试验标注界面的任务**（标签、说明、字段顺序经常调整）。
3. **流程探索期任务**（优先验证“标注规范是否可执行、结果是否可导出”）。

### 12.4 哪些任务后续可能更适合 doccano

下一轮建议重点比较以下场景：

1. **标准化文本分类任务**：界面需求固定、标签结构简单时，doccano 可能更轻量。
2. **强调标注员快速上手的任务**：若目标是缩短操作路径，需对比两者的人机交互成本。
3. **低配置复杂度任务**：当不依赖复杂自定义控件时，可评估 doccano 的效率优势。

结论应是“按任务选平台”，而不是单平台替代：复杂可配置优先看 Label Studio，标准化轻量任务重点对比 doccano。

### 12.5 当前导出结构的不足

当前导出结构主要存在：

1. **字段层级不统一**：任务原始字段、标注结果、元信息在后处理时仍需手工映射。
2. **跨任务 schema 未收敛**：不同 `task_type` 的结果字段未形成统一解析标准。
3. **评测侧字段欠缺**：缺少统一标签编码、冲突标记、配置版本等工程化字段。
4. **复现实验信息不足**：导出结果与“标注配置版本/规则版本”的绑定不够显式。

### 12.6 下一轮建议优化方向（含 doccano 对比）

为保持“AI评测工程实践”主线，下一轮建议：

1. **先定义跨平台统一导出 schema**  
   最小字段建议：`sample_id/task_type/annotator/label/notes(optional)/timestamp/tool/config_version`。

2. **做同数据子集 A/B 对比（Label Studio vs doccano）**  
   使用同一批 day31 子集，比较：导入摩擦、标注时长、误标率、导出可解析性。

3. **补齐一致性最小流程**  
   引入小规模双标与分歧记录，为下一步 Kappa 与误差分析提供数据基础。

4. **建立版本化记录**  
   对标注指南、界面配置、导出映射表分别编号，确保后续迭代可追溯。

> 阶段结论：Day33 已完成“工具闭环可用性验证”；下一轮应转向“跨工具可比较、跨任务可复用、对评测脚本可直接消费”的工程化增强，并以 doccano 对比作为核心推进点。
