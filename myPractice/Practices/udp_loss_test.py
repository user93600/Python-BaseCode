import socket
import time

SERVER=('127.0.0.1',12345)

client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.settimeout(0.5)

TOTAL=10000
received=0

start=time.time()
for i in range(TOTAL):
    msg=f"PACKET-{i}"
    client.sendto(msg.encode(),SERVER)

    try:
        data,addr=client.recvfrom(1024)
        if data.decode()==msg:
            received+=1
        
    except socket.timeout:
        pass

end=time.time()

lost=TOTAL-received
lost_rate=lost/TOTAL*100

print(f"发送：{TOTAL}个数据报")
print(f"收到：{received}个回声")
print(f"丢失：{lost}个")
print(f"丢包率：{lost_rate:.2f}%")
print(f"总耗时：{end-start:.2f}秒")
client.close()