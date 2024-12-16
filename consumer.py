import json
import grpc
import pika
import service_pb2
import service_pb2_grpc


def process_message(ch, method, properties, body):
    # Декодирование сообщения из RabbitMQ
    message = json.loads(body)
    print(f"Received message: {message}")

    # Преобразование сообщения в gRPC-запрос
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

    # Вызов gRPC-сервера
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = service_pb2_grpc.CheckServiceStub(channel)
        response = stub.CreateCheck(request)

        print(f"Check created at: {response.file_path}")


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
