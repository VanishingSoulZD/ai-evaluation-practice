from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    """
    数据模型：
    - name: 数据名称
    - value: 数据数值
    """

    name: str
    value: int


@app.post("/upload")
async def upload_item(item: Item):
    """
    上传数据接口：
    接收 Item 数据并返回确认消息和原始数据
    """

    return {"message": "Data received", "data": item.dict()}
