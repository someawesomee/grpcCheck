import json
import pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Модели данных для REST API
class Item(BaseModel):
    name: str
    price: float
    quantity: int

class CreateCheckRequest(BaseModel):
    order_id: int
    items: List[Item]

# Инициализируем FastAPI
app = FastAPI()

# Функция для отправки сообщения в RabbitMQ
def send_to_rabbitmq(queue_name: str, message: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Объявляем очередь (если ее еще нет)
        channel.queue_declare(queue=queue_name)

        # Отправляем сообщение
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Делает сообщение персистентным
            )
        )

        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RabbitMQ error: {str(e)}")

# REST API эндпоинт
@app.post("/create-check/")
async def create_check(request: CreateCheckRequest):
    # Преобразуем запрос в JSON
    message = {
        "order_id": request.order_id,
        "items": [item.dict() for item in request.items]
    }

    # Отправляем сообщение в RabbitMQ
    send_to_rabbitmq(queue_name="check_queue", message=message)

    return {"message": "Request sent to RabbitMQ"}