import socket
import matplotlib.pyplot as plt
import time
import paho.mqtt.client as mqtt

MQTT_BROKER="127.0.0.1"
MQTT_PORT=1883
MQTT_TOPIC='data/number'

mqtt_client=mqtt.Client()
mqtt_client.connect(MQTT_BROKER,MQTT_PORT,60)
mqtt_client.loop_start()

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("127.0.0.1",8888))
server.listen(1)
print("等待客户端连接")

conn,addr=server.accept()
reader=conn.makefile('r',encoding='utf-8')
print(f"客户端{addr}已连接")

plt.ion()
data=[]
fig=plt.figure()

while True:
    #line=conn.recv(1024)
    t0=time.time()
    line=reader.readline()
    t1=time.time()
    if not plt.fignum_exists(fig.number):
        break

    if not line:
        print("客户端断开连接")
        break
    try:
        num=int(line.strip())
    except:
        continue
    
    t2=time.time()

    try:
        mqtt_client.publish(MQTT_TOPIC,str(num))
        print(f"mqtt发布{num}")
    except Exception as e:
        print(f"mqtt发布失败:{e}")

    data.append(num)
    if len(data)>20:
        data.pop(0)

    plt.clf()
    plt.plot(data)
    plt.ylim(0,100)
    plt.pause(0.05)
    t3=time.time()
    print(f"readline:{t1-t0:.3f}s\ndata:{t2-t1:.3f}s\npicture:{t3-t2:.3f}s")

mqtt_client.loop_stop()
mqtt_client.disconnect()
conn.close()
server.close()