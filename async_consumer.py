import json
import pika
import service_pb2
from server import CheckService

def process_message(ch, method, properties, body):
    # Декодирование сообщения
    message = json.loads(body)
    request = service_pb2.CreateCheckRequest(
        order_id=message['order_id'],
        items=[
            service_pb2.Item(
                name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
            for item in message['items']
        ]
    )

    # Формирование чека
    service = CheckService()
    response = service.CreateCheck(request, None)
    print(f"Check created: {response.file_path}")

def consume_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Объявление очереди
    channel.queue_declare(queue='check_queue')

    print("Waiting for messages in 'check_queue'...")
    channel.basic_consume(queue='check_queue', on_message_callback=process_message, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    consume_queue()