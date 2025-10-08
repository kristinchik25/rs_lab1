# rs_lab1

# Лабораторная работа 01. Реализация RPC-сервиса с использованием gRPC

## Цели
- Освоить принципы удаленного вызова процедур (RPC) и их применение в распределенных системах;
- Изучить основы фреймворка gRPC и языка определения интерфейсов Protocol Buffers (Protobuf);
- Научиться определять сервисы и сообщения с помощью Protobuf;
- Реализовать клиент-серверное приложение на языке Python с использованием gRPC;
- Получить практические навыки в генерации кода, реализации серверной логики и клиентских вызовов для различных типов RPC.

## Предметная область
Вариант 12, геосервис 

## Описание сервиса и его методов
Сервис GeoService:

 Метод TrackMovement(stream Coordinates) для
отслеживания перемещения объекта в
реальном времени (Bidirectional streaming
RPC).

## Архитектура
В основе лабораторной работы лежит классическая клиент-серверная архитектура (Client-Server Architecture), реализованная с помощью парадигмы удаленного вызова процедур (Remote Procedure Call - RPC).

### 1. Компоненты 
##### Сервер. Это независимое приложение (server.py), которое выполняет основную "бизнес-логику"
Возможности: 
- Предоставляет сервис. Он реализует и "выставляет наружу" сервис, определенный в контракте.
- Обрабатывает запросы. Он слушает входящие сетевые соединения на определенном порту (50051) и обрабатывает вызовы от клиентов.
- Выполняет логику. 
(дописать!!)
  
- Асинхронность. Использует пул потоков (futures.ThreadPoolExecutor) для одновременной обработки нескольких клиентских запросов.

##### Клиент. Это приложение (client.py), которое потребляет функциональность, предоставляемую сервером.
Возможности:
- Инициирует соединение. Устанавливает соединение с сервером по известному адресу (localhost:50051).
- Вызывает удаленные методы. Обращается к методам сервера так, будто это локальные функции.
- Обрабатывает ответы. Получает и выводит на экран данные, возвращенные сервером.

### 2. Взаимодействие и контракт

## Технологический стек

## Ход работы
# Шаг. 1 Подготовка окружения
Для начала необходимо обновить пакеты и установить python:
```
sudo apt update
```

```
sudo apt install python3 python3-pip python3-venv -y
```
Далее создаем и активируем виртуальное окружение
```
mkdir grpc_geoservice_lab
cd grpc_geoservice_lab
python3 -m venv venv
source venv/bin/activate
```
Устанавливаем библиотеки gRPC
```
pip install grpcio grpcio-tools
```
Результат:
Библиотеки загружены и окружение активировано, можно это понять по слову venv в начале строки

<img width="645" height="306" alt="image" src="https://github.com/user-attachments/assets/14ddfa7d-2662-4d33-997a-eb8e936f0eac" />

# Шаг 2. Определение сервиса в .proto файле
Создаем файл geo_service.proto:
```
// Указываем синтаксис proto3
syntax = "proto3";

// Определяем пакет для нашего сервиса
package geoservice;

// Сервис для отслеживания перемещения объекта в реальном времени
service GeoService {
  // Bidirectional streaming RPC: клиент отправляет поток координат,
  // сервер отвечает потоком подтверждений или уведомлений
  rpc TrackMovement(stream Coordinates) returns (stream MovementResponse);
}

// Сообщение с координатами объекта
message Coordinates {
  double latitude = 1;   // Широта (например, 55.7558)
  double longitude = 2;  // Долгота (например, 37.6176)
  int64 timestamp = 3;   // Время получения координат (Unix timestamp в миллисекундах)
}

// Сообщение-ответ от сервера на каждое обновление координат
message MovementResponse {
  string status = 1;    // Статус обработки: "received", "processed", "alert" и т.д.
  string message = 2;   // Дополнительное пояснение
}
```

# Шаг 3. Генерация кода
Выполняем в терминале команду для генерации Python-классов из .proto файла:

```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. geo_service.proto
```
Результат добавления .proto файла и генерации кода

<img width="181" height="136" alt="image" src="https://github.com/user-attachments/assets/566ab3f2-fe54-41b1-be0d-c115ea901f72" />

# Шаг 4. Реализация сервера
Создаем файлы server.py, client.py и пишем код сервера:
```
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
```
```
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
```
Результат 

<img width="258" height="301" alt="image" src="https://github.com/user-attachments/assets/e39257dc-ec0f-4c7d-a6fd-1c1d83334aba" />

# Шаг 5. Запуск и проверка
Для запуска сервера и клиента необходимо работать в двух терминалах. В первом окружение активировано, поэтому выполняем команду:
```
python3 server.py
```
Результат

<img width="559" height="34" alt="image" src="https://github.com/user-attachments/assets/8b9e8be0-7531-46cb-b9fd-06be7d22d84e" />


Во втором терминале сначала необходимо убедиться, что мы находимся в папке нашего проекта. 
```
cd grpc_geoservice_lab
```
После этого активируем окружение
```
source venv/bin/activate
```
И, наконец, запускаем клиент
```
python3 client.py
```
Результат 

<img width="553" height="349" alt="image" src="https://github.com/user-attachments/assets/928f6890-401d-479b-81ae-0af451078b44" />

## Выводы
```

```
