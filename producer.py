import json
import pika

def send_message(order_id, items):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Объявление очереди
    channel.queue_declare(queue='check_queue')

    # Формирование сообщения
    message = {
        "order_id": order_id,
        "items": items
    }
    channel.basic_publish(exchange='', routing_key='check_queue', body=json.dumps(message))
    print("Message sent to 'check_queue'.")

