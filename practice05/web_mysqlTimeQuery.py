from flask import Flask,jsonify,request
import pymysql
from datetime import datetime
import pwinput

app=Flask(__name__)
DB_CONFIG={
    "database":"tcp_data_db",
    "user":"root",
    "password":pwinput.pwinput("请输入你的密码："),
    "host":"127.0.0.1",
    "port":3306,
    "charset":"utf8mb4"
}

def get_records_by_time(start,end):
    try:

        conn=pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        sql="SELECT id,client_ip,receive_data,create_time FROM tcp_record WHERE create_time >= %s AND create_time <= %s"
        cursor.execute(sql,(start,end))
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        return {"错误":f"数据库密码错误：{str(e)}"}
    

@app.route("/api/records")
def query_records():
    start=request.args.get('start','2020-01-01 00:00:00')
    end=request.args.get('end','2099-12-31 23:59:59')

    try:
        datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
        datetime.strptime(end,"%Y-%m-%d %H:%M:%S")

    except ValueError:
        return jsonify({"error":"时间格式错误，请使用 YYYY-MM-DD HH:MM:SS"}),400
    
    records=get_records_by_time(start,end)
    return jsonify(records)

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
