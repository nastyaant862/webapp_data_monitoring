import paho.mqtt.client as mqtt
import random
import time
from datetime import datetime
from db_actions import insert
#from sensor_data import SensorData
import sys

class SensorData:
    def __init__(self):
        self.temperature = None
        self.time_of_process = None
        self.cacao = None
        self.chocolate_powder = None
        self.aromatizer = None

    def update_data(self, temperature, time_of_process, cacao, chocolate_powder, aromatizer):
        self.temperature = temperature
        self.time_of_process = time_of_process
        self.cacao = cacao
        self.chocolate_powder = chocolate_powder
        self.aromatizer = aromatizer


sensor_data_var = SensorData()

# конфигурация MQTT брокера
MQTT_BROKER = "mqtt.eclipseprojects.io"  # Пример публичного MQTT брокера
MQTT_PORT = 1883  # Порт MQTT брокера
MQTT_KEEP_ALIVE_INTERVAL = 60  # Интервал поддержания соединения

# топики для подписки и публикации
TEMP_TOPIC = "sensor/temperature"
TIME_TOPIC = "sensor/time"
CACAO_TOPIC = "sensor/cacao"
CHOCO_TOPIC = "sensor/chocolate_powder"
AROMA_TOPIC = "sensor/aromatizer"

# функция обработки входящих сообщений
def on_message(client, userdata, msg):
    print(f"Получено сообщение на топик {msg.topic}: {msg.payload.decode()}")
    global sensor_data_var
    if msg.topic == TEMP_TOPIC:
        sensor_data_var.temperature = msg.payload.decode()
    elif msg.topic == TIME_TOPIC:
        sensor_data_var.time_of_process = msg.payload.decode()
    elif msg.topic == CACAO_TOPIC:
        sensor_data_var.cacao = msg.payload.decode()
    elif msg.topic == CHOCO_TOPIC:
        sensor_data_var.chocolate_powder = msg.payload.decode()
    elif msg.topic == AROMA_TOPIC:
        sensor_data_var.aromatizer = msg.payload.decode()

# Функция обработки успешного подключения
def on_connect(client, userdata, flags, rc):
    print(f"Подключение к брокеру завершено с кодом {rc}")
     # Подписка на топики
    client.subscribe(TEMP_TOPIC)
    client.subscribe(TIME_TOPIC)
    client.subscribe(CACAO_TOPIC)
    client.subscribe(CHOCO_TOPIC)
    client.subscribe(AROMA_TOPIC)


# Функция обработки потери соединения
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Соединение с брокером потеряно, пытаемся переподключиться...")
        client.reconnect()

# Эмуляция получения данных с датчиков (температура и время)
def simulate_sensor_data():
    temperature = round(random.uniform(55.0, 75.0), 2)  # Эмуляция температуры
    time_of_process = 3
    cacao = 27
    chocolate_powder = 53
    aromatizer = 100 - cacao - chocolate_powder - 5

    sensor_data_var.update_data(temperature, time_of_process, cacao, chocolate_powder, aromatizer)
    return temperature, time_of_process, cacao, chocolate_powder, aromatizer

# Основная функция
def run_mqtt_client():
    client = mqtt.Client()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEP_ALIVE_INTERVAL)
    client.loop_start()

    try:
        while True:
            # эмуляция получения данных с датчиков
            temperature, time_of_process, cacao, chocolate_powder, aromatizer  = simulate_sensor_data()
            # Публикация данных на топики
            # client.publish(TEMP_TOPIC, f"Температура: {temperature:.2f} °C")
            # client.publish(TIME_TOPIC, f"Время: {time_of_process}")
            # client.publish(CACAO_TOPIC, f"Какао: {cacao}%")
            # client.publish(CHOCO_TOPIC, f"Шоколадный порошок: {chocolate_powder}%")
            # client.publish(AROMA_TOPIC, f"Ароматизатор: {aromatizer}%")
            client.publish(TEMP_TOPIC, temperature)
            client.publish(TIME_TOPIC, time_of_process)
            client.publish(CACAO_TOPIC, cacao)
            client.publish(CHOCO_TOPIC, chocolate_powder)
            client.publish(AROMA_TOPIC, aromatizer)

            # insert(current_time, temperature,'°C', 1)
            # insert(current_time, time_of_process, 'ч', 2)
            # insert(current_time, cacao, '%', 3)
            # insert(current_time, chocolate_powder, '%', 4)
            # insert(current_time, aromatizer, '%', 5)

            # Задержка между публикациями
            time.sleep(10)
    except KeyboardInterrupt:
        print("Завершение работы клиента...")
        #select()
    finally:
        # Остановка клиента и закрытие соединения
        client.loop_stop()
        client.disconnect()

# if __name__ == "__main__":
#     run_mqtt_client()
