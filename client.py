import grpc
import time
import threading

# Импортируем сгенерированные классы
import geo_service_pb2
import geo_service_pb2_grpc


def run():
    # Устанавливаем соединение с сервером
    with grpc.insecure_channel('localhost:50051') as channel:
        # Создаём "заглушку" (stub) для вызова методов сервиса
        stub = geo_service_pb2_grpc.GeoServiceStub(channel)

        print("Начинаем отправку координат объекта...")

        # Генератор координат (имитация GPS-трека)
        def coord_generator():
            coordinates = [
                (55.7558, 37.6176, int(time.time() * 1000)),   # Москва
                (55.7512, 37.6130, int(time.time() * 1000)),   # немного сдвинулись
                (55.7489, 37.6190, int(time.time() * 1000)),   # ещё сдвиг
                (55.7520, 37.6250, int(time.time() * 1000)),   # и т.д.
            ]
            for lat, lon, ts in coordinates:
                print(f" → Отправка координат: {lat}, {lon}")
                yield geo_service_pb2.Coordinates(
                    latitude=lat,
                    longitude=lon,
                    timestamp=ts
                )
                time.sleep(1)  # имитация реального времени между обновлениями

        try:
            # Вызываем bidirectional streaming RPC
            responses = stub.TrackMovement(coord_generator())

            # Получаем и выводим ответы от сервера
            for response in responses:
                print(f" ← Ответ от сервера: [{response.status}] {response.message}")

        except grpc.RpcError as e:
            print(f"Ошибка RPC: {e.status()}: {e.details()}")


if __name__ == '__main__':
    run()