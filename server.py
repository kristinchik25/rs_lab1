# server.py
import grpc
from concurrent import futures
import time
import logging

import geo_service_pb2
import geo_service_pb2_grpc


class GeoServiceServicer(geo_service_pb2_grpc.GeoServiceServicer):
    def TrackMovement(self, request_iterator, context):
        print(" Сервер: начато отслеживание перемещения (ожидание координат от клиента)...")
        try:
            for coord in request_iterator:
                print(f"Сервер получил: {coord.latitude:.4f}, {coord.longitude:.4f} @ {coord.timestamp}")
                response = geo_service_pb2.MovementResponse(
                    status="processed",
                    message=f"[Сервер] Обработаны координаты: ({coord.latitude:.4f}, {coord.longitude:.4f})"
                )
                yield response
        except Exception as e:
            print(f" Сервер: ошибка при обработке потока: {e}")
            yield geo_service_pb2.MovementResponse(
                status="error",
                message="[Сервер] Внутренняя ошибка"
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    geo_service_pb2_grpc.add_GeoServiceServicer_to_server(GeoServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(" Сервер GeoService запущен на порту 50051")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
