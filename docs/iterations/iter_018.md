# Iteration 018 - Day 18: 异步任务入门（Celery/RQ）

## 迭代概述

**主题**：平台接口与异步任务  
**日期**：Day 18  
**目标**：学习并实践异步任务处理大数据集，使用 Celery 或 RQ，将批量指标计算任务异步执行，提升接口响应速度和系统吞吐量。

---

## 背景与目的

在评测和数据处理场景中，批量指标计算可能涉及大量数据，若同步处理会导致接口阻塞或超时。Day 18 任务通过引入异步任务框架（Celery 或 RQ），实现批量指标计算任务的异步执行，解耦接口请求与任务执行，提高系统并发处理能力。

---

## 待解决的问题

- 配置异步任务框架（Celery 或 RQ）
- 封装批量指标计算函数为异步任务
- 调用异步任务接口，异步处理 CSV 文件数据
- 获取并返回异步执行结果

---

## 参考资料

- [Celery 官方文档](https://docs.celeryq.dev/en/stable/)
- [RQ 官方文档](https://python-rq.org/docs/)
- Week 2 & Day 17 模块化指标计算代码
- [FastAPI 与 Celery 集成示例](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

## 任务要求

1. 配置 Celery 或 RQ：
   - 安装依赖：`pip install celery[redis]` 或 `pip install rq redis`
   - 配置消息中间件（如 Redis）
2. 封装异步任务函数：
   - 将批量指标计算逻辑封装为异步任务
   - 支持 CSV 文件路径作为输入
   - 计算完成后返回指标结果或写入结果文件
3. 接口调用异步任务：
   - 提供 FastAPI 接口接收 CSV 上传
   - 上传后立即触发异步任务执行计算
   - 返回任务 ID 或确认信息
4. 验证异步执行：
   - 通过任务 ID 查询任务状态
   - 异步任务完成后可获取计算结果

---

## 实现步骤

### 1. 安装依赖

```bash
pip install fastapi uvicorn pandas celery redis
```

### 2. 配置消息队列

- 安装并启动 Redis：

```bash
# Linux
redis-server
```

- Celery 配置示例 `celery_app.py`：

```python
from celery import Celery

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
```

### 3. 封装异步任务函数

`tasks.py`：

```python
from celery_app import app
from week2_metrics import MetricsCalculator
import pandas as pd

@app.task
def compute_metrics_task(file_path: str) -> dict:
    df = pd.read_csv(file_path)
    calculator = MetricsCalculator()
    results = [calculator.compute(row.to_dict()) for _, row in df.iterrows()]
    return {"filename": file_path, "metrics": results}
```

### 4. FastAPI 接口触发异步任务

`main.py`：

```python
from fastapi import FastAPI, File, UploadFile
import os
import uuid
from tasks import compute_metrics_task

app = FastAPI()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/batch-metrics-async")
async def batch_metrics_async(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        return {"error": "Only CSV files are allowed"}

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    task = compute_metrics_task.delay(file_location)
    return {"task_id": task.id, "message": "Task submitted successfully"}
```

### 5. 启动服务与 worker

```bash
# 启动 FastAPI
uvicorn main:app --reload

# 启动 Celery worker
celery -A tasks worker --loglevel=info
```

### 6. 验证异步任务

- 通过返回的 `task_id` 查询任务状态：

```python
from tasks import compute_metrics_task
result = compute_metrics_task.AsyncResult(task_id)
if result.ready():
    print(result.get())
```

---

## 验收标准

- `POST /batch-metrics-async` 接口可用
- 上传 CSV 文件后，异步任务成功执行批量指标计算
- 任务可查询状态，完成后返回正确结果
- Swagger UI 可用，可直接上传文件并获取任务 ID
- 异步处理大文件时接口立即返回，任务在后台执行完成

---

## 迭代备注

- 可扩展支持任务队列优先级、重试机制
- 可与 Day 17 批量计算接口兼容
- 后续迭代可实现异步结果文件下载或通知机制
