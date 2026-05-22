# Iteration 019 - Day 19：异步任务与报告生成

## 背景/目的

在 Day 18 中我们实现了异步批量指标计算，本次任务旨在将异步任务的计算结果进一步处理，自动生成 CSV 数据报告和图表，实现指标计算到可视化报告的闭环，提高工作流自动化能力。

## 解决问题

- 异步完成大规模指标计算后，结果无法直接用于分析
- 人工整理 CSV 或绘图效率低，容易出错
- 需要自动化生成可存档和可分享的报告

## 参考资料

- FastAPI 文档：[https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Celery 文档：[https://docs.celeryq.dev](https://docs.celeryq.dev)
- Pandas 官方教程：[https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- Matplotlib / Seaborn 绘图文档

## 任务要求

- 异步任务完成指标计算后生成报告文件
- 报告包括：
  - CSV 文件，包含所有计算结果
  - 图表（可使用 Matplotlib/Seaborn）
- 文件存储在 `reports/` 目录下，使用 UUID 或时间戳确保唯一性
- 提供 FastAPI 接口触发异步任务并返回任务 ID
- 提供任务状态查询接口，任务完成后返回报告文件路径

## 实现步骤

1. **创建报告存储目录**

   ```python
   import os
   REPORT_DIR = "./reports"
   os.makedirs(REPORT_DIR, exist_ok=True)
   ```

2. **封装异步任务函数**
   - 文件：`tasks.py`
   - 异步任务内容：
     - 调用 Day 17/18 指标计算逻辑
     - 生成 CSV 文件保存到 `reports/`
     - 使用 Matplotlib/Seaborn 绘制图表并保存（png/pdf）
     - 返回生成文件路径

   示例：

   ```python
   import pandas as pd
   import uuid
   import matplotlib.pyplot as plt
   import seaborn as sns
   from celery_app import app
   from week2_metrics import MetricsCalculator

   @app.task
   def compute_metrics_and_report(file_path: str) -> dict:
       try:
           df = pd.read_csv(file_path)
           calculator = MetricsCalculator()
           results = [calculator.compute(row.to_dict()) for _, row in df.iterrows()]
           results_df = pd.DataFrame(results)

           report_id = str(uuid.uuid4())
           csv_path = f"./reports/report_{report_id}.csv"
           results_df.to_csv(csv_path, index=False)

           # 绘制图表示例
           plt.figure(figsize=(8,6))
           sns.histplot(results_df['accuracy'], bins=10)
           plt.title("Accuracy Distribution")
           chart_path = f"./reports/chart_{report_id}.png"
           plt.savefig(chart_path)
           plt.close()

           return {"csv": csv_path, "chart": chart_path}

       except Exception as e:
           return {"error": str(e)}
   ```

3. **FastAPI 接口触发异步报告生成**

   ```python
   from fastapi import FastAPI, File, UploadFile
   import uuid, os
   from tasks import compute_metrics_and_report

   app = FastAPI()
   UPLOAD_DIR = "./uploads"
   os.makedirs(UPLOAD_DIR, exist_ok=True)

   @app.post("/batch-report-async")
   async def batch_report_async(file: UploadFile = File(...)):
       if not file.filename.lower().endswith(".csv"):
           return {"error": "Only CSV files are allowed"}

       filename = f"{uuid.uuid4()}_{file.filename}"
       file_location = os.path.join(UPLOAD_DIR, filename)
       with open(file_location, "wb") as f:
           f.write(await file.read())

       task = compute_metrics_and_report.delay(file_location)
       return {"task_id": task.id, "message": "Report generation task submitted"}
   ```

4. **查询异步任务状态**

   ```python
   @app.get("/report-tasks/{task_id}")
   def get_report_task_status(task_id: str):
       result = compute_metrics_and_report.AsyncResult(task_id)
       response = {"task_id": task_id, "status": result.status}
       if result.status == "FAILURE":
           response["error"] = str(result.result)
       if result.status == "SUCCESS":
           response["result"] = result.get()
       return response
   ```

5. **启动服务和 worker**

   ```bash
   # 启动 FastAPI
   uvicorn main:app --reload

   # 启动 Celery worker
   celery -A tasks worker --loglevel=info
   ```

## 验收标准

- `/batch-report-async` 接口可用，上传 CSV 后立即返回任务 ID
- 异步任务后台生成 CSV + 图表报告，结果正确
- `/report-tasks/{task_id}` 查询任务状态可获得生成文件路径
- 所有文件存储在 `reports/`，名称唯一
- Swagger UI 可用，支持上传 CSV 并触发报告生成
