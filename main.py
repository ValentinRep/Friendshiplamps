import random
import sys
import json
import time
import datetime
import multiprocessing
import communication.mqtt.mqtt_publisher as mqtt_publisher
import communication.mqtt.mqtt_subscriber as mqtt_subscriber
from multiprocessing import Queue
from communication import encryption_utility


def generateJSONButtonMessage(lightEnabled, HWID):
    currentTime = datetime.datetime.now()
    encrypedID = encryption_utility.encryptString(key, "Friendshiplamps" + str(currentTime))
    ID = encrypedID.decode()
    data = {'ID': ID, 'HWID': HWID, 'Time': currentTime.timestamp(), 'enabled:': lightEnabled}
    message = json.dumps(data)
    return message

def pushed():
    print("Lampe wird aktiviert")

def shutdown():
    print("Lampe wird ausgeschalten")


if __name__ == '__main__':
    MQTT_SERVER = 'test.mosquitto.org'  # MQTT Server
    port = 1883
    MQTT_PATH = "friendshiplamps"  # Das Topic

    publisher = mqtt_publisher.MqttPublisher(MQTT_SERVER, port, MQTT_PATH)

    # Encryption Area
    key = encryption_utility.read_key('main/key.key');
    HWID = encryption_utility.generate_key('crazy').decode();
    message = generateJSONButtonMessage(False, HWID)
    ch = True

    q = Queue()
    p1 = multiprocessing.Process(target=mqtt_subscriber.subscribe, args=(MQTT_SERVER, port, MQTT_PATH, q))
    p1.start()

    isPushed = False
    pushedTime = round(time.time())


    while True:
        try:
            if random.randrange(0, 1) == 0:
                if not isPushed:
                    pushedTime = round(time.time())
                    pushed()
                    isPushed = True
                if(pushedTime + 5 >= round(time.time())):
                    shutdown()
            else:
                if isPushed:
                    isPushed = False
                    pushed()

            if(q.empty()):
                print('leer')
            else:
                print(q.get())
            if ch:
                ch = False
                message = generateJSONButtonMessage(True, HWID)
            else:
                ch = True
                message = generateJSONButtonMessage(False, HWID)

            # print("send:" + message)
            publisher.publish(message)
            time.sleep(1)
        except KeyboardInterrupt:
            print('Fehler')
            sys.exit()
