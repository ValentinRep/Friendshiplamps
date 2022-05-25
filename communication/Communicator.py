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
        self.HWID = encryption_utility.generate_key('PC').decode();
        self.messages = []
        self.publisher = mqtt_pubisher.MqttPublisher(MQTT_SERVER, port, MQTT_PATH)
        self.messageIDs = []
        self.q = Queue()
        self.p1 = multiprocessing.Process(target=mqtt_subscriber.subscribe, args=(self.MQTT_SERVER, self.port, self.MQTT_PATH, self.q))
        self.p1.start()

    def processMessages(self):
        self.deleteOldMessageIDs()
        currentTime = datetime.datetime.now().timestamp()
        while not self.q.empty():
            isValidatedTopic = False
            isNewMessage = False
            isMyHWID = False
            data = json.loads(self.q.get().decode())
            for key, value in data.items():
                decryptedKey = encryption_utility.decryptToBytes(self.key, value.encode())
                if key == "ID":
                    if decryptedKey.startswith(self.MQTT_PATH):
                        isValidatedTopic = True
                    if decryptedKey == self.HWID:
                        isMyHWID = False
                if key == "timestamp":
                    try:
                        timestampFloat = float(decryptedKey)
                        if currentTime - timestampFloat > 10:
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
            if isValidatedTopic and not isMyHWID and isNewMessage:
                self.messages.append(json.loads(data.get("message")))

    #Die IDs werden 10 Sekunden gespeichert, damit nicht jemand anderes die selbe MQTT-Nachricht erneut senden kann und
    # somit den Partner-Clinet vortäuschen kann. Nachrichten älter als 10 Sekunden werden nicht verarbeitet!
    def deleteOldMessageIDs(self):
        currentTime = datetime.datetime.now().timestamp()
        for value in self.messageIDs:
            valueTime = float(value)
            if currentTime - valueTime >= 10:
                self.messageIDs.remove(value)


    def hasMessages(self):
        self.processMessages()
        return len(self.messages) > 0

    def getMessages(self):
        self.processMessages()
        oldMessages = self.messages.copy()
        self.messages.clear()
        return oldMessages

    def publish(self, **kwargs):
        mqtt_message_values = kwargs
        raw_message = json.dumps(kwargs)

        currentTime = str(datetime.datetime.now().timestamp())
        mqtt_message_values["ID"] = self.MQTT_PATH + currentTime
        mqtt_message_values["timestamp"] = currentTime
        mqtt_message_values["HWID"] = self.HWID
        mqtt_message_values["message"] = raw_message

        for key, value in mqtt_message_values.items():
            mqtt_message_values[key] = encryption_utility.encryptString(self.key, str(value)).decode()
        mqtt_message = json.dumps(mqtt_message_values)

        self.publisher.publish(mqtt_message)



