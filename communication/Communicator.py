import communication.mqtt.mqtt_publisher as mqtt_pubisher
import communication.mqtt.mqtt_subscriber as mqtt_subscriber
import multiprocessing
from multiprocessing import Queue
from communication import encryption_utility
import json
import datetime


class Comunicator:
    def __init__(self, message_lifetime, key, client_name, MQTT_SERVER, port, MQTT_PATH):
        self.message_lifetime = message_lifetime
        self.key = key
        self.client_name = client_name

        self.MQTT_SERVER = MQTT_SERVER
        self.port = port
        self.MQTT_PATH = MQTT_PATH

        self.messages = []
        self.messageIDs = []
        self.publisher = mqtt_pubisher.MqttPublisher(MQTT_SERVER, port, MQTT_PATH)

        #Der MQTT-Subscriber muss in einen neuen Prozess gestartet werden, da sonst das Programm auf eine Nachricht
        #warten würde.
        self.q = Queue()
        self.p1 = multiprocessing.Process(target=mqtt_subscriber.subscribe, args=(self.MQTT_SERVER, self.port, self.MQTT_PATH, self.q))
        self.p1.start()

    def processMessages(self):
        self.deleteOldMessageIDs()
        currentTime = datetime.datetime.now().timestamp()
        while not self.q.empty():
            isValidatedTopic = False
            isNewMessage = False
            isMyClient_name = False
            data = json.loads(self.q.get().decode())
            for key, value in data.items():
                decryptedKey = encryption_utility.decryptToBytes(self.key, value.encode())
                if key == "ID":
                    if decryptedKey.startswith(self.MQTT_PATH):
                        isValidatedTopic = True
                    if decryptedKey == self.client_name:
                        isMyClient_name = False
                if key == "timestamp":
                    try:
                        timestampFloat = float(decryptedKey)
                        if currentTime - timestampFloat > self.message_lifetime:
                            isNewMessage = False
                        else:
                            if value in self.messageIDs:
                                isNewMessage = False
                            else:
                                isNewMessage = True
                            self.messageIDs.append(decryptedKey)
                    except ValueError:
                        print("Timestamp ist keine float")
                data[key] = decryptedKey
            if isValidatedTopic and not isMyClient_name and isNewMessage:
                self.messages.append(json.loads(data.get("message")))

    #Die IDs werden 10 Sekunden gespeichert, damit nicht jemand anderes die selbe MQTT-Nachricht erneut senden kann und
    # somit den Partner-Clinet vortäuschen kann. Nachrichten älter als 10 Sekunden werden nicht verarbeitet!
    def deleteOldMessageIDs(self):
        currentTime = datetime.datetime.now().timestamp()
        for value in self.messageIDs:
            valueTime = float(value)
            if currentTime - valueTime >= self.message_lifetime:
                self.messageIDs.remove(value)


    def hasMessages(self):
        if not self.q.empty() or len(self.messages) >= 1:
            return True
        return False

    def getMessages(self):
        self.processMessages()
        oldMessages = self.messages.copy()
        self.messages.clear()
        return oldMessages

    def publish(self, **kwargs):
        mqtt_message_values = {}
        raw_message = json.dumps(kwargs)

        currentTime = str(datetime.datetime.now().timestamp())
        mqtt_message_values["ID"] = self.MQTT_PATH + currentTime
        mqtt_message_values["timestamp"] = currentTime
        mqtt_message_values["HWID"] = self.client_name
        mqtt_message_values["message"] = raw_message

        for key, value in mqtt_message_values.items():
            mqtt_message_values[key] = encryption_utility.encryptString(self.key, str(value)).decode()
        mqtt_message = json.dumps(mqtt_message_values)

        self.publisher.publish(mqtt_message)



