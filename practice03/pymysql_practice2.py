import pymysql

DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    "password":input("请输入您的root密码："),
    "database":"tcp_data_db",
    "port":3306,
    "charset":"utf8mb4"
}

def insert_tcp_data(client_ip,data):
    conn=None
    cursor=None
    try:
        conn=pymysql.connect(**DB_CONFIG)

        cursor=conn.cursor()

        sql="INSERT INTO tcp_record (client_ip,receive_data) VALUES (%s,%s)"

        cursor.execute(sql,(client_ip,data))

        conn.commit()
        print(f"数据插入成功，影响行数：{cursor.rowcount}")
        print(f"新纪录ID：{cursor.lastrowid}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"数据插入失败：{type(e).__name__}-{e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__=="__main__":
    insert_tcp_data("192.168.1.100","Hello MySQL from Python")