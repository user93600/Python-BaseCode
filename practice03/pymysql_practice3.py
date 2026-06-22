import pymysql
DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    "password":input("请输入密码："),
    "database":"tcp_data_db",
    "port":3306,
    "charset":"utf8mb4"
}

def batch_insert_tcp_data(data_list):
    conn=None
    cursor=None
    try:
        conn=pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor()

        sql="INSERT INTO tcp_record (client_ip,receive_data) VALUES (%s,%s)"

        cursor.executemany(sql,data_list)

        conn.commit()
        print(f"插入成功，共插入{cursor.rowcount}条数据")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"插入失败：{type(e).__name__}-{e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def query_all_data():
    conn=None
    cursor=None

    try:
        conn=pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor()

        sql="SELECT * FROM tcp_record ORDER BY create_time DESC"
        cursor.execute(sql)

        results=cursor.fetchall()

        print("\n所有tcp记录：")
        print("-"*80)
        print(f"{'ID':<5}{'客户端IP':<20}{'接收时间':<20}{'数据内容'}")
        print("-"*80)

        for row in results:
            record_id,client_ip,receive_data,create_time=row
            print(f"{record_id:<5}{client_ip:<20}{create_time.strftime('%Y-%m-%D %H:%M:%S'):<20}{receive_data}")

        print("-"*80)
        print(f"共查询到{len(results)}条记录")

    except Exception as e:
        print(f"查询失败：{type(e).__name__}-{e}")
    
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

if __name__=="__main__":
    test_data = [
        ("192.168.1.102", "批量数据1"),
        ("192.168.1.103", "批量数据2"),
        ("192.168.1.104", "批量数据3"),
        ("192.168.1.105", "批量数据4"),
        ("192.168.1.106", "批量数据5")
    ]
    batch_insert_tcp_data(test_data)
    query_all_data()