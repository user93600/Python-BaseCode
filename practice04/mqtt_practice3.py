import paho.mqtt.client as mqtt

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print("已连接成功")
    else:
        print(f"连接失败，错误码{rc}")
    
client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect=on_connect
client.connect("127.0.0.1",1883,60)

client.loop_forever()