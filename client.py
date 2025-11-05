# client.py
import grpс
import time
import geo_service_pb2
import geo_service_pb2_grpc


def coord_generator():
    """Генератор координат — клиент ничего не обрабатывает, только отправляет."""
    coords = [
        (55.7558, 37.6176),
        (55.7512, 37.6130),
        (55.7489, 37.6190),
        (55.7520, 37.6250),
    ]
    for i, (lat, lon) in enumerate(coords):
        ts = int((time.time() + i) * 1000)
        print(f"Клиент отправляет: {lat:.4f}, {lon:.4f}")
        yield geo_service_pb2.Coordinates(latitude=lat, longitude=lon, timestamp=ts)
        time.sleep(1)


def run():
    print("Подключение к серверу GeoService на localhost:50051...")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = geo_service_pb2_grpc.GeoServiceStub(channel)

        try:
            print("Начинаем отправку координат...")
            responses = stub.TrackMovement(coord_generator())

            print("Ожидание ответов от сервера...")
            for response in responses:
                print(f"Ответ от СЕРВЕРА: [{response.status}] {response.message}")

        except grpc.RpcError as e:
            print(f"ОШИБКА: не удалось подключиться к серверу или вызвать метод")
            print(f"   Код: {e.code()}, детали: {e.details()}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


if __name__ == '__main__':
    run()

