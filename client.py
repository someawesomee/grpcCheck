import grpc
import service_pb2
import service_pb2_grpc

def create_check():
    # Устанавливаем соединение с сервером
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = service_pb2_grpc.CheckServiceStub(channel)

        # Данные для чека
        items = [
            service_pb2.Item(name="big+mac", price=12.0, quantity=2),
            service_pb2.Item(name="big_special", price=23.0, quantity=1)
        ]

        request = service_pb2.CreateCheckRequest(order_id=123, items=items)

        # Отправляем запрос и получаем ответ
        response = stub.CreateCheck(request)

        # Выводим путь к файлу чека
        print(f"Check created at: {response.file_path}")

if __name__ == "__main__":
    create_check()