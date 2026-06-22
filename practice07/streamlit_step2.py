import streamlit as st
import pandas as pd
import pymysql
from pwinput import pwinput

DB_CONFIG={
    "host":"127.0.0.1",
    "user":"root",
    "password":pwinput("请输入你的密码："),
    "port":3306,
    "charset":"utf8mb4",
    "database":"tcp_data_db"
}

def load_data():
    """从mysql加载所有记录，返回dataframe"""
    conn=pymysql.connect(**DB_CONFIG)
    query="""
    SELECT id,client_ip,receive_data,create_time 
    FROM tcp_record 
    WHERE create_time >= NOW() - INTERVAL 7 DAY
    ORDER BY create_time
    """
    df=pd.read_sql(query,conn)
    conn.close()
    return df

st.title("原始数据查看")
df=load_data()
if df.empty:
    st.warning("最近一周没有数据")
    st.stop()

df['receive_data']=pd.to_numeric(df['receive_data'],errors='coerce')
df=df.dropna(subset=['receive_data'])

if df.empty:
    st.warning("没有有效的数值")
    st.stop()

col1,col2,col3=st.columns(3)
col1.metric("平均值",round(df['receive_data'].mean(),2))
col2.metric("最大值",df["receive_data"].max())
col3.metric("最小值",df["receive_data"].min())


st.write(f"共{len(df)}条记录")
st.dataframe(df)

st.subheader("时间序列趋势")
st.line_chart(df.set_index('create_time')['receive_data'])

st.subheader("数值分布")
st.bar_chart(df['receive_data'].value_counts(bins=10).sort_index())