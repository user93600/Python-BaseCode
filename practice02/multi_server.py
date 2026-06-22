import socket
import threading
import matplotlib.pyplot as plt

all_data={}
data_lock=threading.Lock()
colors=['limegreen','cyan','magenta','yellow','orange','pink']
color_idx=0

def handle_client(conn,addr):
    global color_idx
    with data_lock:
        color=colors[color_idx%len(colors)]
        color_idx+=1
    data =[]
    print(f"[+]客户端{addr}已连接，颜色{color}")

    try:
        while True:
            raw=conn.recv(1024)
            if not raw:
                break
            try:
                num=int(raw.decode())
            except:
                continue

            data.append(num)
            if len(data)>20:
                data.pop(0)

            with data_lock:
                all_data[str(addr)]=(list(data),color)

    except ConnectionResetError:
        print(f"客户端{addr}强制断开")
    finally:
        conn.close()
        with data_lock:
            all_data.pop(str(addr),None)
        print(f"[-]客户端{addr}已移除")

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(('0.0.0.0',12345))
    server.listen(5)
    print("多客户端已启动，等待连接")
    plt.ion()
    fig=plt.figure()
    ax=fig.add_subplot(111)
    ax.set_ylim(0,100)

    while True:
        if not plt.fignum_exists(fig.number):
            print("窗口关闭，服务端退出")
            break
        server.settimeout(0.1)
        try:
            conn,addr=server.accept()
            t=threading.Thread(target=handle_client,args=(conn,addr),daemon=True)
            t.start()
        except socket.timeout:
            pass

        ax.clear()
        with data_lock:
            for client_addr,(data,color) in all_data.items():
                if data:
                    ax.plot(data,color=color,linewidth=2,label=client_addr)
        
        ax.legend(loc='upper right',fontsize='small')
        ax.set_yilm(0,100)
        plt.pause(0.05)
    server.close()

if __name__=="__main__":
    main()


