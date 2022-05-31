import paho.mqtt.client as mqtt


class MqttPublisher:

    def __init__(self, mqtt_server, port, mqtt_path):
        self.client = mqtt.Client()
        self.client.MQTT_SERVER = mqtt_server
        self.client.port = port

        self.mqtt_server = mqtt_server
        self.mqtt_path = mqtt_path
        self.port = port

    def publish(self, mess):
        try:
            self.client.connect(self.mqtt_server, self.port)
            self.client.publish(self.mqtt_path, mess)
        except:
            print("Nachricht konnte nicht gesendet werden")