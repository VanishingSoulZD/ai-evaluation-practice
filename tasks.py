import pandas as pd

from celery_app import app
from week2_metrics import MetricsCalculator


@app.task
def compute_metrics_task(file_path: str) -> dict:
    try:
        df = pd.read_csv(file_path)
        calculator = MetricsCalculator()
        results = [calculator.compute(row.to_dict()) for _, row in df.iterrows()]
        return {"filename": file_path, "metrics": results}
    except Exception as e:
        return {"filename": file_path, "error": str(e)}
