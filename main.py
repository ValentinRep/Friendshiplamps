import datetime
import sys
import time
import IO.communication.Communicator as Communicator
import IO.Board
from configparser import ConfigParser

from IO import Board

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
    partner_client_name = config["Partner"]["client_name"]

    encryption_key = config["Encryption"]["key"]
    encryption_salt = config["Encryption"]["salt"]

    ch = True
    isPushed = False
    currentTime = datetime.datetime.now().timestamp()
    firstPushTime = round(time.time())

    partnerCommunicator = Communicator.Comunicator(message_lifetime, encryption_key, partner_client_name, mqtt_server, port, mqtt_path + "/" + partner_client_name)
    ownCommunicator = Communicator.Comunicator(message_lifetime, encryption_key,  client_name, mqtt_server, port, mqtt_path + "/" + client_name)

    board = Board.Board()

    while True:
        if partnerCommunicator.hasMessages():
            messages = partnerCommunicator.getMessages()
            latestMessage = messages[0]
            for message in messages:
                if message.get("timestamp") > latestMessage.get("timestamp"):
                    latestMessage = message
            if latestMessage.get("aktiviert"):
                if not board.isEnabled:
                    board.enableLamp()
            else:
                if board.isEnabled:
                    board.disableLamp()

        currentTime = datetime.datetime.now().timestamp()
        if board.buttonPressed():
            if not isPushed:
                firstPushTime = False
            isPushed = True
        else:
            if isPushed:
                if board.isEnabled:
                    ownCommunicator.publish(aktiviert=False, timestamp=currentTime)
                    board.disableLamp()
                else:
                    ownCommunicator.publish(aktiviert=True, timestamp=currentTime)
                    board.enableLamp()
            isPushed = False
        time.sleep(0.1)
