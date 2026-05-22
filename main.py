import os
import uuid

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from tasks import compute_metrics_and_report, compute_metrics_task
from week2_metrics import MetricsCalculator

app = FastAPI()

UPLOAD_DIR = "./uploads"
REPORT_DIR = "./reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口：
    - 仅接收 CSV 文件
    - 保存到本地 UPLOAD_DIR
    - 返回上传确认信息
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Only CSV files are allowed"})

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"filename": filename, "message": "File uploaded successfully"}


@app.post("/batch-metrics")
async def batch_metrics(file: UploadFile = File(...)):
    """批量指标计算接口。"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Only CSV files are allowed"})

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(file_location)

    calculator = MetricsCalculator()
    results = []
    for _, row in df.iterrows():
        results.append(calculator.compute(row.to_dict()))

    return {"filename": file.filename, "metrics": results}


@app.post("/batch-metrics-async")
async def batch_metrics_async(file: UploadFile = File(...)):
    """异步批量指标计算接口。"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Only CSV files are allowed"})

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    task = compute_metrics_task.delay(file_location)
    return {"task_id": task.id, "message": "Task submitted successfully"}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """查询异步任务状态（非阻塞）。"""
    result = compute_metrics_task.AsyncResult(task_id)

    response = {"task_id": task_id, "status": result.status}
    if result.status == "FAILURE":
        response["error"] = str(result.result)

    return response


@app.post("/batch-report-async")
async def batch_report_async(file: UploadFile = File(...)):
    """上传 CSV 后触发异步报告生成任务。"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Only CSV files are allowed"})

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    task = compute_metrics_and_report.delay(file_location)
    return {"task_id": task.id, "message": "Report generation task submitted"}


@app.get("/report-tasks/{task_id}")
def get_report_task_status(task_id: str):
    """查询报告异步任务状态与结果文件路径。"""
    result = compute_metrics_and_report.AsyncResult(task_id)

    response = {"task_id": task_id, "status": result.status}
    if result.status == "FAILURE":
        response["error"] = str(result.result)
    if result.status == "SUCCESS":
        response["result"] = result.result

    return response
