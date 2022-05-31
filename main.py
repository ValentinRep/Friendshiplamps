import sys
import time
import communication.Communicator as Communicator
from configparser import ConfigParser

if __name__ == '__main__':
    # Lese Konfigurationsdatei
    configFile = "res/config.ini"
    config = ConfigParser()
    config.read(configFile)
    # read Elements of Config
    mqtt_server = config["MQTT-Server"]["address"]
    port = int(config["MQTT-Server"]["port"])
    mqtt_path = config["MQTT-Server"]["mqtt_path"]

    message_lifetime = int(config["Communication"]["message_lifetime"])
    client_name = config["Communication"]["client_name"]

    encryption_key = config["Encryption"]["key"]
    encryption_salt = config["Encryption"]["salt"]

    ch = True
    isPushed = False
    pushedTime = round(time.time())

    communicator = Communicator.Comunicator(message_lifetime, encryption_key, client_name, mqtt_server, port, mqtt_path)

    while True:
        if communicator.hasMessages():
            print(communicator.getMessages()[0])
        else:
            print("no messages")
        try:
            if ch:
                ch = False
                message = communicator.publish(aktiviert=True)
            else:
                ch = True
                message = communicator.publish(aktiviert=False)
            time.sleep(1)
        except KeyboardInterrupt:
            print('Fehler')
            sys.exit()