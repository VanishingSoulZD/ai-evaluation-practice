# Iteration 016 - Day 16: FastAPI 文件上传接口

## 迭代概述

**主题**：平台接口与异步任务  
**日期**：Day 16  
**目标**：通过 FastAPI 构建一个支持 CSV 文件上传的接口，实现文件保存与确认返回，为后续数据处理和异步任务提供基础。

---

## 背景与目的

在应用开发中，文件上传是常见需求，尤其是 CSV 数据文件。Day 16 的任务通过 FastAPI 学习如何接收文件上传、保存到本地，并返回操作结果，进一步掌握接口处理文件和请求的能力。

---

## 待解决的问题

- 快速实现文件上传接口
- 支持 CSV 文件上传并保存到服务器指定目录
- 返回 JSON 格式的操作确认信息

---

## 参考资料

- [FastAPI 文件上传官方文档](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastAPI 上传文件示例](https://fastapi.tiangolo.com/tutorial/request-files/#uploading-files)

---

## 任务要求

1. 编写一个 `POST /upload-file` 接口
2. 接收 CSV 文件上传
3. 将文件保存到本地指定目录（如 `./uploads`）
4. 返回 JSON 响应确认上传成功

---

## 实现步骤

### 1. 安装依赖

确保 FastAPI 与 Uvicorn 已安装：

```bash
pip install fastapi uvicorn
```

### 2. 创建文件上传接口

新建 `main.py`（如果还没有）或在现有项目中新增接口：

```python
from fastapi import FastAPI, File, UploadFile
import os

app = FastAPI()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口：
    - 接收 CSV 文件
    - 保存到本地 UPLOAD_DIR
    - 返回上传确认信息
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "message": "File uploaded successfully"}
```

说明：

- 使用 `UploadFile` 类型接收上传文件
- `File(...)` 用于参数声明，确保必填
- 文件写入使用 `await file.read()` 获取内容
- 上传目录 `./uploads` 若不存在会自动创建

### 3. 启动服务并测试

```bash
uvicorn main:app --reload
```

- 打开浏览器访问 `http://127.0.0.1:8000/docs`
- 使用 Swagger UI 测试 `POST /upload-file` 上传 CSV 文件
- 或用 curl 测试：

```bash
curl -X POST "http://127.0.0.1:8000/upload-file" -F "file=@example.csv"
```

---

## 验收标准

- 服务启动并监听 8000 端口
- `POST /upload-file` 接口可用
- 上传 CSV 文件后，文件成功保存到 `./uploads` 目录
- 返回 JSON 响应示例：

```json
{
  "filename": "example.csv",
  "message": "File uploaded successfully"
}
```

- Swagger UI 可用，可直接发送文件并查看返回

---

## 迭代备注

- 后续可扩展支持多文件上传
- 可以增加文件类型和大小限制
- 后续迭代会结合异步任务处理上传的 CSV 数据
