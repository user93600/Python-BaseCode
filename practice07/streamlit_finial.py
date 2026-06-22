import streamlit as st
import pandas as pd
import pymysql
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=3000,limit=None,key="auto_refresh")

if "is_login" not in st.session_state:
    st.session_state.is_login=False

if not st.session_state.is_login:
    st.title("登录")
    mysql_pwd=st.text_input("请输入密码：",type="password")

    if st.button("登录"):
        try:
            test_conn=pymysql.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                database="tcp_data_db",
                charset="utf8mb4",
                password=mysql_pwd
            )
            test_conn.close()

            st.session_state.is_login=True
            st.session_state.pwd=mysql_pwd
            st.rerun()

        except pymysql.err.OperationalError:
            st.error("密码错误")
    st.stop()
    
    

DB_CONFIG={
    "host":"127.0.0.1",
    "port":3306,
    "user":"root",
    "password":st.session_state.pwd,
    "charset":"utf8mb4",
    "database":"tcp_data_db"
}

@st.cache_data(ttl=2)
def load_data():
    """从MySQL加载最近1小时的数据，返回干净的DataFrame"""
    conn=pymysql.connect(**DB_CONFIG)
    query="""
        SELECT receive_data,create_time
        FROM tcp_record
        WHERE create_time >= NOW() - INTERVAL 1 HOUR
        ORDER BY create_time
    """
    df=pd.read_sql(query,conn)
    conn.close()

    df['receive_data']=pd.to_numeric(df['receive_data'],errors='coerce')
    df['create_time']=pd.to_datetime(df['create_time'])
    df=df.dropna(subset=['receive_data'])
    return df

st.title("动态数据看板")
st.caption("页面每3秒字典刷新，展示最近一小时的统计分析")

df=load_data()

if df.empty:
    st.warning("最近1小时内没有数据，请确保tcp服务端和客户端正在运行")
else:
    st.subheader("实时统计")
    col1,col2,col3,col4=st.columns(4)
    col1.metric("最新数据",int(df['receive_data'].iloc[-1]))
    col2.metric("平均值",round(df['receive_data'].mean(),2))
    col3.metric("最大值",int(df['receive_data'].max()))
    col4.metric("最小值",int(df['receive_data'].min()))

    st.subheader('最近一小时趋势')
    chart_data=df.set_index('create_time')['receive_data']
    st.line_chart(chart_data)

    st.subheader("数值分布")
    hist_data=df['receive_data'].value_counts(bins=10).sort_index()
    st.bar_chart(hist_data)

    st.subheader("最新十条记录")
    st.dataframe(df.tail(10)[['create_time','receive_data']].sort_values('create_time',ascending=False))