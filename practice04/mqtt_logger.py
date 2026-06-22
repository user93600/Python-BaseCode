import paho.mqtt.client as mqtt
from datetime import datetime
import os

os.makedirs("practice04",exist_ok=True)
timestamp=datetime.now().strftime("%Y-%m-%d %H-%M-%S")
LOG_FOLDER=os.path.dirname(__file__)
LOG_FILE=os.path.join(LOG_FOLDER,f'mqtt_data_{timestamp}.log')

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print("文件记录员已连接，订阅频道data/number")
        client.subscribe("data/number")

    else:
        print(f"连接失败，rc={rc}")

def on_message(client,userdata,msg):
    data_str=msg.payload.decode()
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line=f"{timestamp}|{data_str}\n"

    with open(LOG_FILE,"a",encoding='utf-8') as f:
        f.write(log_line)
    print(f"已记录：{log_line.strip()}")

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect=on_connect
client.on_message=on_message

client.connect("127.0.0.1",1883,60)
print("文件记录员已启动，等待广播...")
client.loop_forever()
