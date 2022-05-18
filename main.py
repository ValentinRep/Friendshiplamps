import sys
import time
import communication.Communicator as Communicator

if __name__ == '__main__':
    MQTT_SERVER = 'test.mosquitto.org'  # MQTT Server
    port = 1883
    MQTT_PATH = "friendshiplamps"  # Das Topic

    ch = True
    isPushed = False
    pushedTime = round(time.time())

    communicator = Communicator.Comunicator(MQTT_SERVER, port, MQTT_PATH)

    while True:
        communicator.processMessages()
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
