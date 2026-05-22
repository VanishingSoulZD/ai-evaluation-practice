# Iteration 015 - Day 15: FastAPI 入门与简单接口

## 迭代概述

**主题**：平台接口与异步任务  
**日期**：Day 15  
**目标**：通过 FastAPI 构建一个简单的上传数据并返回结果的接口，为后续异步任务和复杂接口打基础。

---

## 背景与目的

在现代应用中，服务端接口是各类系统交互的基础。本次迭代通过 FastAPI 学习如何快速构建 HTTP 接口，实现数据上传与结果返回，掌握基础的请求处理与 JSON 响应，为后续多工具协作 Agent 平台接口开发打基础。

---

## 待解决的问题

- 快速掌握 FastAPI 的基本用法
- 实现一个简单的数据上传→处理→返回结果流程
- 能够在本地启动服务并通过 HTTP 请求访问接口

---

## 参考资料

- [FastAPI 官方教程](https://fastapi.tiangolo.com/)
- [FastAPI 入门示例](https://fastapi.tiangolo.com/tutorial/)

---

## 任务要求

1. 搭建 FastAPI 项目环境
2. 编写一个上传数据并返回处理结果的接口
3. 能够在本地通过浏览器或工具（Postman/curl）访问接口
4. 接口返回 JSON 格式的数据

---

## 实现步骤

### 1. 安装 FastAPI 与 Uvicorn

```bash
pip install fastapi uvicorn
```

- `fastapi`：核心框架
- `uvicorn`：用于本地启动 FastAPI 服务的 ASGI 服务器

### 2. 创建最简单的接口

新建 `main.py`：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    value: int

@app.post("/upload")
async def upload_item(item: Item):
    return {"message": "Data received", "data": item}
```

说明：

- 定义了一个 `POST /upload` 接口
- 使用 Pydantic 的 `BaseModel` 进行数据验证
- 返回 JSON 格式响应

### 3. 启动服务并测试

```bash
uvicorn main:app --reload
```

- 打开浏览器访问 `http://127.0.0.1:8000/docs`
- 使用 Swagger UI 测试 `POST /upload` 接口
- 也可用 curl 测试：

```bash
curl -X POST "http://127.0.0.1:8000/upload" -H "Content-Type: application/json" -d '{"name": "test", "value": 123}'
```

---

## 验收标准

- 服务能够启动并监听 8000 端口
- 浏览器或工具能够访问 `POST /upload` 接口
- 接口返回示例 JSON 数据：

```json
{
  "message": "Data received",
  "data": {
    "name": "test",
    "value": 123
  }
}
```

- Swagger UI 可用，可直接在页面发送请求并查看返回

---

## 迭代备注

- 可进一步扩展为上传文件接口或多参数接口
- 后续迭代将结合异步任务处理，学习后台任务和长时间运行接口的实现方式
