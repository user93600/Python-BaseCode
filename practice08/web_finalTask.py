from flask import Flask,jsonify,request
import pymysql
import pwinput
from datetime import datetime

app=Flask(__name__)

DB_CONFIG={
    "database":"tcp_data_db",
    "user":"root",
    "port":3306,
    "charset":"utf8mb4",
    "host":"127.0.0.1",
    "password":pwinput.pwinput("请输入密码：")
}

def query_db(start,end):
    conn=pymysql.connect(**DB_CONFIG)
    cursor=conn.cursor(pymysql.cursors.DictCursor)
    sql="""
        SELECT id,client_ip,receive_data,create_time
        FROM tcp_record
        WHERE create_time >= %s AND create_time <=%s
        ORDER BY create_time
        """
    cursor.execute(sql,(start,end))
    rows=cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.route('/api/records')
def get_records():
    start=request.args.get('start','2020-01-01 00:00:00')
    end=request.args.get('end','2099-12-31 23:59:59')

    for time_str in (start,end):
        try:
            datetime.strptime(time_str,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error":f"时间格式错误{time_str},请使用YYYY-MM-DD HH:MM:SS"}),400
        
    if start > end:
        return jsonify({"error":"起始时间不能晚于结束时间"}),400
    
    data=query_db(start,end)
    return jsonify(data)

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)