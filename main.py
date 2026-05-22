import os
import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
