import streamlit as st
import pandas as pd
import pymysql
from datetime import datetime,timedelta
from pwinput import pwinput
import pymysql.err
import plotly.express as px

if "is_login" not in st.session_state:
    st.session_state.is_login=False

if not st.session_state.is_login:
    st.title("登录")
    mysql_pwd=st.text_input("请输入密码：",type="password")

    if st.button("登录"):
        try:
            test_conn=pymysql.connect(
                database="tcp_data_db",
                port=3306,
                charset="utf8mb4",
                password=mysql_pwd,
                user="root",
                host="127.0.0.1"
            )
            test_conn.close()

            st.session_state.is_login=True
            st.session_state.pwd=mysql_pwd
            st.rerun()

        except pymysql.err.OperationalError:
            st.error("密码错误，请重新输入")
    st.stop()

# if not mysql_pwd:
#     st.warning("等待密码输入后查看...")
#     st.stop()

DB_CONFIG={
    "database":"tcp_data_db",
    "port":3306,
    "charset":"utf8mb4",
    "password":st.session_state.pwd,
    "user":"root",
    "host":"127.0.0.1"
}

def load_data(start_data,end_data,client_ip=None):
    conn=pymysql.connect(**DB_CONFIG)
    sql="""
    SELECT id,client_ip,receive_data,create_time
    FROM tcp_record
    WHERE create_time >= %s AND create_time <= %s
    """
    params=[start_data,end_data]
    if client_ip and client_ip !="全部":
        sql+=" AND client_ip = %s"
        params.append(client_ip)
    sql+=" ORDER BY create_time"
    df=pd.read_sql(sql,conn,params=params)
    conn.close()
    return df

@st.cache_data
def get_client_list():
    conn=pymysql.connect(**DB_CONFIG)
    df=pd.read_sql("SELECT DISTINCT client_ip FROM tcp_record",conn)
    conn.close()
    return ["全部"]+df['client_ip'].tolist()

st.title("数据查询")

st.sidebar.header("筛选条件")
today=datetime.now().date()
start=st.sidebar.date_input("开始日期",today-timedelta(days=7))
end=st.sidebar.date_input("结束日期",today)
client_list=get_client_list()
selected_client=st.sidebar.selectbox("客户端IP",client_list)

start_str=start.strftime('%Y-%m-%d')+' 00:00:00'
end_str=end.strftime("%Y-%m-%d")+" 23:59:59"

df=load_data(start_str,end_str,selected_client if selected_client!="全部" else None)

if df.empty:
    st.warning(f"没有符合条件的数据")
else:
    st.write(f"查询到{len(df)}条记录")
    st.dataframe(df.head(50))

    st.subheader("趋势图")
    fig = px.line(
        df, 
        x="create_time", 
        y="receive_data",
        title="数据趋势"
    )
    fig.update_layout(yaxis=dict(tick0=0, dtick=10))
    st.plotly_chart(fig, use_container_width=True)