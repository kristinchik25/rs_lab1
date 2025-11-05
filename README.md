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
Сервер (Server). Это независимое приложение (server.py), которое выполняет основную «бизнес-логику» геосервиса.

Возможности:
- Предоставляет сервис. Реализует и «выставляет наружу» сервис GeoService, определённый в контракте .proto-файла.
- Обрабатывает запросы. Слушает входящие сетевые соединения на порту 50051 и принимает поток координат от клиентов.
- Выполняет логику. В реальном времени обрабатывает каждую поступающую пару координат (широта, долгота, временная метка), имитируя работу системы отслеживания перемещения объекта (например, транспорта).
- Поддерживает двунаправленный поток. На каждое входящее сообщение сервер немедленно формирует и отправляет клиенту ответное сообщение с подтверждением обработки.
- Многопоточность. Использует пул потоков (futures.ThreadPoolExecutor) для одновременной обработки нескольких клиентских соединений.

Клиент (Client). Это приложение (client.py), которое потребляет функциональность, предоставляемую сервером.

Возможности:
- Инициирует соединение. Устанавливает gRPC-соединение с сервером по адресу localhost:50051.
- Отправляет поток данных. Формирует и передаёт серверу последовательность географических координат в виде streaming-запроса, имитируя движение объекта.
- Получает поток ответов. Одновременно читает и обрабатывает streaming-ответы от сервера, демонстрируя работу двунаправленного канала связи.
- Имитирует реальное поведение. Между отправками координат вставляются задержки (time.sleep), что моделирует поступление данных от GPS-трекера в реальном времени.

### 2. Взаимодействие и контракт

Ключевым элементом архитектуры является сервисный контракт (Service Contract), определённый в файле geo_service.proto.

Роль контракта. Этот файл выступает в роли «единого источника правды» для API. Он строго и однозначно описывает:

- Какие сервисы доступны (в данном случае это сервис GeoService)
- Какие методы можно вызывать (реализован один метод: TrackMovement)
- Формат данных — чётко определены структуры сообщений:

   a) Coordinates — содержит географические координаты объекта (широта, долгота) и временную метку

   b) MovementResponse — содержит статус обработки и текстовое сообщение от сервера

  <img width="571" height="411" alt="image" src="https://github.com/user-attachments/assets/d12641b4-72f3-4c67-9198-78a3e6c51647" />


## Технологический стек

1.Язык определения интерфейсов (IDL): Protocol Buffers (Protobuf)

2.Фреймворк RPC: gRPC

3.Транспортный протокол: HTTP/2

4.Язык программирования: Python 3

5.Ключевые библиотеки Python:

   a) grpcio
   
   b) grpcio-tools
   
6.Среда выполнения и изоляция:

   a) ОС: Ubuntu 20.04 (Linux).
   
   b) Виртуальное окружение (venv). Инструмент для изоляции зависимостей
проекта, гарантирующий, что установленные пакеты (grpcio и др.) не будут
конфликтовать с системными или другими проектами.


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
```
```
# client.py
import grpc
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
<img width="899" height="424" alt="image" src="https://github.com/user-attachments/assets/061c9966-9438-4580-b991-4f4286f3f0e6" />

## Выводы

В ходе выполнения лабораторной работы был успешно разработан и протестирован клиент-серверный сервис GeoService с использованием gRPC. 
Лабораторная работа позволила на практике изучить полный цикл создания gRPC-сервиса — от проектирования API до его реализации и тестирования. Созданное приложение полностью соответствует поставленному заданию и демонстрирует ключевые преимущества gRPC: высокую производительность, компактную сериализацию, строгую типизацию и гибкость в выборе модели взаимодействия
