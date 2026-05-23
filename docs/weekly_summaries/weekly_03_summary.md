# Iteration 021 Summary（Day 21）

## Week3 总览（Day 15 ~ Day 20）

Week3 已完成从「基础 API」到「异步报告闭环」的完整建设，形成了可落地的数据处理流程：

**CSV 上传 → 指标计算（同步/异步）→ 报告生成 → 任务状态查询**。

---

## 1) Day 15 ~ Day 20 任务完成情况汇总

| Day | 主题 | 完成内容 | 当前状态 |
| --- | --- | --- | --- |
| Day 15 | FastAPI 入门接口 | 完成基础 `POST /upload`，实现 JSON 请求与响应、Swagger 调试 | ✅ 已完成 |
| Day 16 | 文件上传接口 | 完成 `POST /upload-file`，支持 CSV 上传并保存到 `uploads/` | ✅ 已完成 |
| Day 17 | 批量指标计算 API | 完成 `POST /batch-metrics`，可读取 CSV 并按行计算指标后返回 JSON | ✅ 已完成 |
| Day 18 | 异步任务入门 | 引入 Celery + Redis，完成 `POST /batch-metrics-async` 异步提交与任务 ID 返回 | ✅ 已完成 |
| Day 19 | 异步报告生成 | 完成 `POST /batch-report-async`，异步生成 CSV 报告与图表；支持任务状态查询 | ✅ 已完成 |
| Day 20 | 接口+异步综合 | 完成 `POST /process-csv-async` 端到端整合；支持 `/process-tasks/{task_id}` 查询最终报告路径 | ✅ 已完成 |

---

## 2) 模块整理（API 接口 / 异步任务 / 指标计算 / 报告生成）

### 2.1 API 接口模块（`main.py`）

建议保留并统一以下核心接口：

- `POST /upload-file`：上传 CSV 文件
- `POST /batch-metrics`：同步批量指标计算
- `POST /batch-metrics-async`：异步批量指标计算
- `POST /batch-report-async`：异步报告生成
- `POST /process-csv-async`：端到端异步处理（推荐主入口）
- `GET /tasks/{task_id}`、`GET /report-tasks/{task_id}`、`GET /process-tasks/{task_id}`：任务状态查询

### 2.2 异步任务模块（`tasks.py`）

建议统一任务定义：

- `compute_metrics_task(file_path)`：异步指标计算
- `compute_metrics_and_report(file_path)`：异步计算 + CSV/图表报告生成

任务返回结构建议统一为：

```json
{
  "task_id": "xxx",
  "status": "PENDING|STARTED|SUCCESS|FAILURE",
  "result": {
    "csv": "./reports/report_xxx.csv",
    "chart": "./reports/chart_xxx.png"
  },
  "error": null
}
```

### 2.3 指标计算模块（如 `week2_metrics.py`）

建议持续保持「模块化可复用」：

- 提供统一类：`MetricsCalculator`
- 提供统一方法：`compute(record: dict) -> dict`
- 指标输入输出字段明确，避免接口层重复编写计算逻辑

### 2.4 报告生成模块（可在 `tasks.py` 或独立 `reporting/`）

建议包含两类产物：

- CSV 报告：汇总所有行的指标结果
- 图表报告：指标分布图（例如 accuracy 直方图）

报告目录建议固定：

- `uploads/`：原始上传文件
- `reports/`：生成的 CSV 与图表

---

## 3) 使用说明概览

### 3.1 依赖安装

```bash
pip install fastapi uvicorn pandas celery redis matplotlib seaborn
```

### 3.2 服务启动命令

```bash
# 1) 启动 Redis（示例）
redis-server

# 2) 启动 FastAPI
uvicorn main:app --reload

# 3) 启动 Celery Worker
celery -A tasks worker --loglevel=info
```

### 3.3 接口调用说明（含示例）

#### A. 上传文件接口

```bash
curl -X POST "http://127.0.0.1:8000/upload-file" -F "file=@example.csv"
```

示例返回：

```json
{
  "filename": "example.csv",
  "message": "File uploaded successfully"
}
```

#### B. 同步批量指标计算

```bash
curl -X POST "http://127.0.0.1:8000/batch-metrics" -F "file=@example.csv"
```

示例返回（节选）：

```json
{
  "filename": "example.csv",
  "metrics": [
    {"accuracy": 0.95, "f1": 0.91},
    {"accuracy": 0.89, "f1": 0.87}
  ]
}
```

#### C. 异步报告生成

```bash
curl -X POST "http://127.0.0.1:8000/batch-report-async" -F "file=@example.csv"
```

示例返回：

```json
{
  "task_id": "9db9f2cc-xxxx-xxxx-xxxx-14f2b5c9a113",
  "message": "Report generation task submitted"
}
```

### 3.4 异步任务查询

```bash
curl "http://127.0.0.1:8000/process-tasks/9db9f2cc-xxxx-xxxx-xxxx-14f2b5c9a113"
```

- `PENDING/STARTED`：任务执行中
- `SUCCESS`：返回报告路径（CSV + 图表）
- `FAILURE`：返回错误信息

示例成功返回：

```json
{
  "task_id": "9db9f2cc-xxxx-xxxx-xxxx-14f2b5c9a113",
  "status": "SUCCESS",
  "result": {
    "csv": "./reports/report_9db9f2cc.csv",
    "chart": "./reports/chart_9db9f2cc.png"
  }
}
```

---

## 4) 代码与目录整理建议

### 4.1 统一目录结构（建议）

```text
project/
├── main.py
├── tasks.py
├── week2_metrics.py
├── celery_app.py
├── uploads/
├── reports/
├── docs/
│   └── iterations/
│       ├── iter_015.md
│       ├── ...
│       └── iter_021_summary.md
└── requirements.txt / pyproject.toml
```

### 4.2 注释规范

- 接口函数：说明输入、处理流程、返回字段、异常分支
- 异步任务：说明任务参数、耗时点、返回结构
- 指标函数：说明指标含义、计算公式（如适用）

### 4.3 文件命名规范

- 接口文件：`main.py`（单入口）或 `api_*.py`（拆分后）
- 任务文件：`tasks.py`、`task_*.py`
- 报告文件：`report_<uuid>.csv`、`chart_<uuid>.png`
- 上传文件：`<uuid>_<origin_name>.csv`（避免重名覆盖）

---

## 5) 验收标准说明

本周成果建议按以下标准验收：

1. **文档完整**
   - 包含启动说明、接口清单、示例调用、状态查询说明。
2. **接口可直接运行**
   - 按启动命令执行后，可通过 Swagger/curl 成功调用。
3. **示例请求返回正确**
   - 上传、同步计算、异步提交、状态查询均返回预期字段。
4. **异步流程闭环可验证**
   - 可从 `task_id` 查询到 `SUCCESS`，并获得 `reports/` 中 CSV 与图表路径。

---

## 结论

Week3 已完成「接口化 + 异步化 + 报告化」的核心里程碑，具备可演示、可复用、可扩展的基础能力。Day 21 的重点是文档与结构收敛，确保团队成员可在最短时间内完成环境搭建、接口联调与流程验收。
