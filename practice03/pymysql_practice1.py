import pymysql
try:
    conn=pymysql.connect(
        host='127.0.0.1',
        user='root',
        password=input("请输入您的root密码："),
        database='tcp_data_db',
        port=3306,
        charset='utf8mb4'
    )
    print("数据库连接成功")
    conn.close()
    print("连接已关闭")
except Exception as e:
    print(f"数据库连接失败：{type(e).__name__}-{e}")