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
