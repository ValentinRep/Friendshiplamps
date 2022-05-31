import communication.mqtt.mqtt_publisher as mqtt_publisher
import communication.mqtt.mqtt_subscriber as mqtt_subscriber
import multiprocessing
from multiprocessing import Queue
from communication import encryption_utility
import json
import datetime


class Comunicator:
    def __init__(self, message_lifetime, key, client_name, mqtt_server, port, mqtt_path):
        self.message_lifetime = message_lifetime
        self.key = key
        self.client_name = client_name

        self.MQTT_SERVER = mqtt_server
        self.port = port
        self.MQTT_PATH = mqtt_path

        self.messages = []
        self.messageIDs = []
        self.publisher = mqtt_publisher.MqttPublisher(mqtt_server, port, mqtt_path)

        # Der MQTT-Subscriber muss in einen neuen Prozess gestartet werden, da sonst das Programm auf eine Nachricht
        # warten würde.
        self.q = Queue()
        self.p1 = multiprocessing.Process(target=mqtt_subscriber.subscribe,
                                          args=(self.MQTT_SERVER, self.port, self.MQTT_PATH, self.q))
        self.p1.start()

    def processMessages(self):
        self.deleteOldMessageIDs()
        current_time = datetime.datetime.now().timestamp()
        while not self.q.empty():
            is_validated_topic = False
            is_new_message = False
            is_my_client_name = False
            data = json.loads(self.q.get().decode())
            for key, value in data.items():
                decrypted_key = encryption_utility.decryptToBytes(self.key, value.encode())
                if key == "ID":
                    if decrypted_key.startswith(self.MQTT_PATH):
                        is_validated_topic = True
                    if decrypted_key == self.client_name:
                        is_my_client_name = False
                if key == "timestamp":
                    try:
                        timestamp_float = float(decrypted_key)
                        if current_time - timestamp_float > self.message_lifetime:
                            is_new_message = False
                        else:
                            if value in self.messageIDs:
                                is_new_message = False
                            else:
                                is_new_message = True
                            self.messageIDs.append(decrypted_key)
                    except ValueError:
                        print("Timestamp ist keine float")
                data[key] = decrypted_key
            if is_validated_topic and not is_my_client_name and is_new_message:
                self.messages.append(json.loads(data.get("message")))

    # Die IDs werden 10 Sekunden gespeichert, damit nicht jemand anderes die selbe MQTT-Nachricht erneut senden kann und
    # somit den Partner-Clinet vortäuschen kann. Nachrichten älter als 10 Sekunden werden nicht verarbeitet!
    def deleteOldMessageIDs(self):
        current_time = datetime.datetime.now().timestamp()
        for value in self.messageIDs:
            value_time = float(value)
            if current_time - value_time >= self.message_lifetime:
                self.messageIDs.remove(value)

    def hasMessages(self):
        if not self.q.empty() or len(self.messages) >= 1:
            return True
        return False

    def getMessages(self):
        self.processMessages()
        old_messages = self.messages.copy()
        self.messages.clear()
        return old_messages

    def publish(self, **kwargs):
        mqtt_message_values = {}
        raw_message = json.dumps(kwargs)

        current_time = str(datetime.datetime.now().timestamp())
        mqtt_message_values["ID"] = self.MQTT_PATH + current_time
        mqtt_message_values["timestamp"] = current_time
        mqtt_message_values["HWID"] = self.client_name
        mqtt_message_values["message"] = raw_message

        for key, value in mqtt_message_values.items():
            mqtt_message_values[key] = encryption_utility.encryptString(self.key, str(value)).decode()
        mqtt_message = json.dumps(mqtt_message_values)

        self.publisher.publish(mqtt_message)
