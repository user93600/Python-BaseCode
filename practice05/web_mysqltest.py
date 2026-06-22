from flask import Flask,jsonify,request,render_template_string
import pwinput
import pymysql

app=Flask(__name__)

DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    #"password":pwinput.pwinput("请输入你的密码："),
    "database":"tcp_data_db",
    "port":3306,
    "charset":"utf8mb4"
}

def get_all_records(db_password):
    db_config=DB_CONFIG.copy()
    db_config['password'] = db_password
    conn=pymysql.connect(**db_config)
    cursor=conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id,client_ip,receive_data,create_time FROM tcp_record")
    rows=cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.route('/')
def index():
    # 极简HTML密码框，直接写在代码里，不用新建文件
    html = '''
    <h1>数据库登录</h1>
    <form action="/query" method="post">
        请输入MySQL密码：<input type="password" name="password" required>
        <button type="submit">查询数据</button>
    </form>
    '''
    return render_template_string(html)

@app.route("/query",methods=['POST'])
def show_records():
    try:
        db_password=request.form.get('password')
        records=get_all_records(db_password)
        return jsonify(records)
    except Exception as e:
        return jsonify({
            "msg":f"连接失败:{str(e)}"
        })
    
    

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)