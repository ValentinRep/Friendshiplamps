import paho.mqtt.client as mqtt


class MqttPublisher:

    def __init__(self, MQTT_SERVER, port, MQTT_PATH):
        self.client = mqtt.Client()
        self.client.MQTT_SERVER = MQTT_SERVER
        self.client.port = port

        self.MQTT_SERVER = MQTT_SERVER
        self.MQTT_PATH = MQTT_PATH
        self.port = port

    def publish(self, mess):
        try:
            self.client.connect(self.MQTT_SERVER, self.port)
            self.client.publish(self.MQTT_PATH, mess)
        except:
            pass