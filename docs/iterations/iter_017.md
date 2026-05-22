# Iteration 017 - Day 17: 批量指标计算 API

## 迭代概述

**主题**：平台接口与异步任务  
**日期**：Day 17  
**目标**：基于 Week 2 的模块化指标计算代码，实现一个接口，能够接收上传的 CSV 文件，批量计算指标，并返回 JSON 或表格形式的结果。

---

## 背景与目的

在评测场景中，用户通常会上传一批数据文件，需要快速计算多个指标。Day 17 的任务通过 FastAPI 构建批量指标计算接口，实现上传 CSV → 批量计算 → 返回结果的完整流程，提升自动化和接口可用性。

---

## 待解决的问题

- 接收 CSV 文件上传并解析数据
- 调用已有的模块化指标计算类对每行数据进行批量计算
- 将计算结果以 JSON 或表格返回给调用方

---

## 参考资料

- [FastAPI 文件上传官方文档](https://fastapi.tiangolo.com/tutorial/request-files/)
- Week 2 模块化指标代码及文档
- [Python pandas CSV 处理文档](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html)

---

## 任务要求

1. 编写一个 `POST /batch-metrics` 接口
2. 接收 CSV 文件上传
3. 将 CSV 数据导入为 DataFrame 或列表
4. 调用已有指标计算类，对每条数据计算指标
5. 返回 JSON 格式结果（可选返回表格或 Excel 文件）

---

## 实现步骤

### 1. 导入依赖

```bash
pip install fastapi uvicorn pandas
```

### 2. 创建接口

新建或更新 `main.py`：

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
import os
from week2_metrics import MetricsCalculator  # 假设 Week2 模块化指标类路径

app = FastAPI()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/batch-metrics")
async def batch_metrics(file: UploadFile = File(...)):
    """
    批量指标计算接口：
    - 接收 CSV 文件上传
    - 调用指标计算类对每条数据计算指标
    - 返回 JSON 格式结果
    """
    if not file.filename.lower().endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Only CSV files are allowed"})

    # 保存上传文件
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # 读取 CSV
    df = pd.read_csv(file_location)

    # 调用指标计算类
    calculator = MetricsCalculator()
    results = []
    for _, row in df.iterrows():
        metrics = calculator.compute(row.to_dict())
        results.append(metrics)

    return {"filename": file.filename, "metrics": results}
```

### 3. 启动服务并测试

```bash
uvicorn main:app --reload
```

- 打开浏览器访问 `http://127.0.0.1:8000/docs`
- 使用 Swagger UI 测试上传 CSV 文件并查看批量指标计算结果
- 或通过 curl 测试：

```bash
curl -X POST "http://127.0.0.1:8000/batch-metrics" -F "file=@example.csv"
```

---

## 验收标准

- 服务启动并监听 8000 端口
- `POST /batch-metrics` 接口可用
- 上传 CSV 文件后，能够成功调用指标计算类计算所有数据行的指标
- 返回 JSON 格式结果示例：

```json
{
  "filename": "example.csv",
  "metrics": [
    { "metric1": 0.95, "metric2": 0.87 },
    { "metric1": 0.89, "metric2": 0.92 }
  ]
}
```

- Swagger UI 可用，能够直接上传 CSV 并查看返回结果

---

## 迭代备注

- 可进一步支持返回 Excel 文件或直接下载结果
- 可增加 CSV 文件大小限制或异步任务处理大文件
- 为后续 A/B 测试和自动化评测流程奠定基础
