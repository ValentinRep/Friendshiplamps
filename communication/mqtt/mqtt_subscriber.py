import paho.mqtt.client as mqtt
from multiprocessing import Queue

#Methode subscribed eine Topic auf einem MQTT-Server und schreibt dieses in den MQTT-Server
def subscribe(MQTT_SERVER, port, mqtt_path, q):
    subscriber = MqttSubscriber(MQTT_SERVER, port, mqtt_path, q)
    subscriber.proc_subscribe()


class MqttSubscriber:

    def __init__(self, MQTT_SERVER, port, MQTT_PATH, q):
        self.MQTT_PATH = MQTT_PATH
        self.MQTT_SERVER = MQTT_SERVER
        self.port = port
        self.q = q
        print('Initialisierung vom MQTT subscriber')

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.MQTT_PATH)


    def on_message(self, client, userdata, msg):
        recived = msg.topic + " " + str(msg.payload)
        self.q.put(recived)

    def proc_subscribe(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.MQTT_SERVER, self.port, 60)
        client.loop_forever()
