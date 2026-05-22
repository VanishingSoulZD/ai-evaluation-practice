import os
import uuid

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from celery_app import app
from week2_metrics import MetricsCalculator

REPORT_DIR = "./reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@app.task
def compute_metrics_task(file_path: str) -> dict:
    """Day 18：异步批量指标计算任务。"""
    try:
        df = pd.read_csv(file_path)
        calculator = MetricsCalculator()
        results = [calculator.compute(row.to_dict()) for _, row in df.iterrows()]
        return {"filename": file_path, "metrics": results}
    except Exception as e:
        return {"filename": file_path, "error": str(e)}


@app.task
def compute_metrics_and_report(file_path: str) -> dict:
    """Day 19：异步计算指标并自动生成 CSV 与图表报告。"""
    try:
        df = pd.read_csv(file_path)
        calculator = MetricsCalculator()
        results = [calculator.compute(row.to_dict()) for _, row in df.iterrows()]
        results_df = pd.DataFrame(results)

        report_id = str(uuid.uuid4())
        csv_path = os.path.join(REPORT_DIR, f"report_{report_id}.csv")
        chart_path = os.path.join(REPORT_DIR, f"chart_{report_id}.png")

        results_df.to_csv(csv_path, index=False)

        plt.figure(figsize=(10, 6))
        # 尝试选取第一个数值型指标用于绘图，确保兼容不同指标结构
        numeric_cols = results_df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            metric_col = numeric_cols[0]
            sns.histplot(results_df[metric_col], bins=10, kde=True)
            plt.title(f"{metric_col} Distribution")
            plt.xlabel(metric_col)
            plt.ylabel("Count")
        else:
            # 若没有可绘制的数值列，生成提示图避免任务失败
            plt.text(0.5, 0.5, "No numeric metrics available for chart", ha="center", va="center")
            plt.title("Metrics Chart")
            plt.axis("off")

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return {"csv": csv_path, "chart": chart_path}
    except Exception as e:
        return {"error": str(e)}
