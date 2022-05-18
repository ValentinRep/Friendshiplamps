import communication.mqtt.mqtt_publisher as mqtt_pubisher
import communication.mqtt.mqtt_subscriber as mqtt_subscriber
import multiprocessing
from multiprocessing import Queue
from communication import encryption_utility
import json
import datetime


class Comunicator:
    def __init__(self, MQTT_SERVER, port, MQTT_PATH):
        self.MQTT_SERVER = MQTT_SERVER
        self.port = port
        self.MQTT_PATH = MQTT_PATH
        self.key = encryption_utility.read_key('res/key.key');
        self.HWID = encryption_utility.generate_key('crazy').decode();
        self.messages = []
        self.publisher = mqtt_pubisher.MqttPublisher(MQTT_SERVER, port, MQTT_PATH)
        self.q = Queue()
        self.p1 = multiprocessing.Process(target=mqtt_subscriber.subscribe, args=(self.MQTT_SERVER, self.port, self.MQTT_PATH, self.q))
        self.p1.start()

    def processMessages(self):
        while not self.q.empty():
            data = json.loads(self.q.get().decode())
            for key, value in data.items():
                data[key] = encryption_utility.decryptToBytes(self.key, value.encode())
            self.messages.append(data)

    def hasMessages(self):
        self.processMessages()
        return len(self.messages) > 0

    def getMessages(self):
        self.processMessages()
        oldMessages = self.messages.copy()
        self.messages.clear()
        return oldMessages

    def publish(self, **kwargs):
        if "ID" in kwargs or "timestamp" in kwargs or "HWID" in kwargs:
            raise ValueError("ID, HWID und timestamp werden von der Methode publish selber generiert")
        currentTime = str(datetime.datetime.now().timestamp())
        kwargs["ID"] = "Friendshiplamps" + currentTime
        kwargs["timestamp"] = currentTime
        kwargs["HWID"] = self.HWID
        for key, value in kwargs.items():
            kwargs[key] = encryption_utility.encryptString(self.key, str(value)).decode()
        message = json.dumps(kwargs)
        self.publisher.publish(message)



