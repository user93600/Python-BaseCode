import paho.mqtt.client as mqtt
import time
import random

client =mqtt.Client()

client.connect("127.0.0.1",1883,60)

client.loop_start()

try:
    while True:
        num=random.randint(0,100)
        client.publish("data/number",str(num))
        print(f"已广播到data/number:{num}")
        time.sleep(1)
except KeyboardInterrupt:
    print("停止广播")
    client.loop_stop()
    client.disconnect()