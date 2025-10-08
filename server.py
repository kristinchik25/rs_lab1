import grpc
from concurrent import futures
import time
import logging

# Импортируем сгенерированные классы
import geo_service_pb2
import geo_service_pb2_grpc


# Класс GeoServiceServicer реализует логику нашего сервиса
class GeoServiceServicer(geo_service_pb2_grpc.GeoServiceServicer):

    # Реализация Bidirectional Streaming RPC метода
    def TrackMovement(self, request_iterator, context):
        """
        Клиент отправляет поток координат (Coordinates),
        сервер отвечает потоком подтверждений (MovementResponse).
        """
        print("Начато отслеживание перемещения объекта...")
        try:
            # Перебираем все входящие сообщения от клиента
            for coord in request_iterator:
                print(f"Получены координаты: широта={coord.latitude}, долгота={coord.longitude}, время={coord.timestamp}")

                # Здесь можно добавить свою логику:
                # - проверка на выход из зоны
                # - сохранение в базу
                # - детекция аномалий и т.д.

                # Формируем ответное сообщение
                response = geo_service_pb2.MovementResponse(
                    status="processed",
                    message=f"Координаты ({coord.latitude:.4f}, {coord.longitude:.4f}) успешно обработаны"
                )

                # Отправляем ответ клиенту
                yield response

        except Exception as e:
            print(f"Ошибка при обработке потока: {e}")
            # Можно отправить финальный ответ об ошибке, если нужно
            yield geo_service_pb2.MovementResponse(
                status="error",
                message="Произошла ошибка на сервере"
            )


def serve():
    # Создаём gRPC-сервер с пулом потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Регистрируем наш сервис на сервере
    geo_service_pb2_grpc.add_GeoServiceServicer_to_server(
        GeoServiceServicer(), server
    )
    
    # Привязываем сервер к порту 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Сервер GeoService запущен на порту 50051...")
    
    # Ждём завершения работы (сервер работает бесконечно)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()