import paho.mqtt.client as mqtt
import time

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print("已连接，发布一条消息....")
        client.publish("test/hello","你好，mqtt")

    else:
        print(f"连接失败，rc={rc}")

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect=on_connect
client.connect("127.0.0.1",1883,60)

client.loop_start()
time.sleep(1)
client.loop_stop()
client.disconnect()
print("消息已发布，程序退出")
