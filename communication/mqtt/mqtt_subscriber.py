import paho.mqtt.client as mqtt


# Methode subscribed eine Topic auf einem MQTT-Server und schreibt dieses in den MQTT-Server
def subscribe(mqtt_server, port, mqtt_path, q):
    subscriber = MqttSubscriber(mqtt_server, port, mqtt_path, q)
    subscriber.proc_subscribe()


class MqttSubscriber:

    def __init__(self, mqtt_server, port, mqtt_path, q):
        self.mqtt_path = mqtt_path
        self.mqtt_server = mqtt_server
        self.port = port
        self.q = q

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.mqtt_path)

    def on_message(self, client, userdata, msg):
        self.q.put(msg.payload)

    def proc_subscribe(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.mqtt_server, self.port, 60)
        client.loop_forever()
