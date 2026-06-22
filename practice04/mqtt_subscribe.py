import paho.mqtt.client as mqtt

def on_connect(client,userdata,flag,rc):
    print(f"连接结果码：{rc}")
    if rc==0:
        print("成功连上 EMQX")
        client.subscribe("data/number")
        print("已发起订阅请求：data/number")
    else:
        print(f"连接失败，错误码：{rc}")

def on_subscribe(client,userdata,mid,granted_qos):
    print(f"订阅成功！主题data/number，服务器分配Qos:{granted_qos}")

def on_message(client,userdata,msg):
    print(f"收到消息:[{msg.topic}]{msg.payload.decode('utf-8')}")

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

client.on_connect=on_connect
client.on_subscribe=on_subscribe
client.on_message=on_message

print("正在连接 EMQX...")
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()