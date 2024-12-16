import os
from concurrent import futures
import grpc
import service_pb2
import service_pb2_grpc

# Папка для сохранения чеков
CHECKS_DIR = "checks"
os.makedirs(CHECKS_DIR, exist_ok=True)  # Убедитесь, что папка создается


# Реализация сервиса gRPC
class CheckService(service_pb2_grpc.CheckServiceServicer):
    def CreateCheck(self, request, context):
        # Генерация имени файла
        file_name = f"check_{request.order_id}.txt"
        file_path = os.path.join(CHECKS_DIR, file_name)

        try:
            # Формирование чека
            with open(file_path, "w") as file:
                file.write(f"Order ID: {request.order_id}\n")
                file.write("Items:\n")
                for item in request.items:
                    file.write(f"- {item.name} x{item.quantity}: ${item.price:.2f}\n")
                total = sum(item.price * item.quantity for item in request.items)
                file.write(f"Total: ${total:.2f}\n")

            # Лог успешного создания файла
            print(f"Check successfully created: {file_path}")

            # Возврат пути к файлу
            return service_pb2.CreateCheckResponse(file_path=os.path.abspath(file_path))
        except Exception as e:
            # Лог ошибок
            print(f"Error while creating check: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.CreateCheckResponse(file_path="")

# Функция запуска сервера
def serve():
    # Создаем gRPC-сервер
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_CheckServiceServicer_to_server(CheckService(), server)

    # Настройка порта
    server.add_insecure_port("[::]:50051")
    print("gRPC server is running on port 50051...")

    # Запуск сервера
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server stopped gracefully.")


if __name__ == "__main__":
    serve()
