# Day34：doccano 最小安装与启动说明（MVP）

## 1. doccano 简介（简短）

doccano 是一个开源的数据标注工具，常用于 NLP 场景（如文本分类、序列标注、Seq2Seq）。本轮目标是跑通本地最小闭环：安装、启动、创建管理员、创建项目、导入样本。

---

## 2. 推荐安装方式（优先 `uv` / `pip`）

> 前提：本机已安装 Python 3.10+ 与 `uv`。

在仓库根目录执行：

```bash
cd /workspace/ai-evaluation-practice

# 创建本地虚拟环境
uv venv

# 在虚拟环境中安装 doccano
uv pip install doccano
```

可选验证：

```bash
cd /workspace/ai-evaluation-practice
uv run doccano --version
```

如果你暂时不用 `uv`，可退化为 `pip`（二选一即可）：

```bash
python -m venv .venv
source .venv/bin/activate
pip install doccano
doccano --version
```

---

## 3. 启动命令

推荐使用默认本地地址启动：

```bash
cd /workspace/ai-evaluation-practice
uv run doccano webserver --port 8000
```

如需后台运行（MVP 不强制）：

```bash
cd /workspace/ai-evaluation-practice
nohup uv run doccano webserver --port 8000 > /tmp/doccano.log 2>&1 &
```

停止服务：

- 前台运行：在终端按 `Ctrl + C`
- 后台运行：`pkill -f "doccano webserver"`

---

## 4. 创建管理员账户

在**另一个终端**执行（首次必做）：

```bash
cd /workspace/ai-evaluation-practice
uv run doccano createuser --username admin --password admin123
```

建议本地 MVP 结束后立刻改成更安全密码。

---

## 5. 打开 Web UI

启动成功后在浏览器访问：

- `http://localhost:8000`

使用上一步创建的管理员账号登录。

---

## 6. 创建项目（Project）

登录后按以下步骤：

1. 点击 **Create** / **New Project**；
2. 填写项目名（建议：`iter034-day31-mvp`）；
3. 选择项目类型（见下一节）；
4. 创建后进入项目主页。

MVP 阶段先建立 1 个项目，不拆多项目协作流程。

---

## 7. 选择项目类型（Project Type）

doccano 常见类型可按任务映射：

- **Text Classification**：文本分类、质量分档、偏好标签；
- **Sequence Labeling**：NER、关键词/片段级标注；
- **Seq2Seq**：问答生成、摘要、改写等“输入→输出”标注。

---

## 8. 本轮推荐项目类型

结合 Day31 样本与 Day32 标注规范，**本轮优先使用 `Text Classification`**：

- 上手最快，最容易先跑通闭环；
- 对 Day31 混合来源样本容错更高；
- 可先完成“可执行标签决策”，后续再扩展到 Sequence Labeling / Seq2Seq。

如果你本轮重点是实体或 span 边界，再单开一个 `Sequence Labeling` 项目即可。

---

## 9. Day31 样本导入建议

### 9.1 推荐导入文件

优先导入：

- `data/day31_samples.jsonl`

备选：

- `data/day31_samples.csv`

建议优先 JSONL，字段结构更稳定、转义问题更少。

### 9.2 导入步骤（MVP）

1. 进入项目；
2. 打开 **Dataset / Import**；
3. 上传 `day31_samples.jsonl`；
4. 导入后先抽查前 5~10 条样本；
5. 确认文本显示、编码、字段完整性正常再开始标注。

### 9.3 导入后最小检查项

- 样本总数与预期一致；
- 中文无乱码；
- 长文本无异常截断；
- `sample_id` 可用于回溯。

---

## 10. 已知限制与注意事项（MVP）

1. **仅本地单机最小流程**：本文件不覆盖生产部署、高可用、集群化。
2. **不展开企业级权限模型**：本轮只需管理员 + 基本项目操作。
3. **不做数据库迁移与性能调优**：先保证流程跑通。
4. **先小批量导入再放量**：先用 10~50 条验证 schema 与标注操作。
5. **端口冲突常见**：若 `8000` 被占用，可换端口（如 `--port 8001`）。
6. **版本差异存在**：不同 doccano 版本在按钮命名或页面布局上可能略有不同，但核心流程一致。

---

## 11. 一条完整启动流程（可直接复制）

```bash
cd /workspace/ai-evaluation-practice
uv venv
uv pip install doccano
uv run doccano createuser --username admin --password admin123
uv run doccano webserver --port 8000
# 打开 http://localhost:8000 并使用 admin 登录
# 创建项目：iter034-day31-mvp
# 项目类型：Text Classification
# 导入：data/day31_samples.jsonl
```
