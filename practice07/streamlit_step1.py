import streamlit as st
import pandas as pd

st.title("📊 数据分析看板")
st.write("欢迎！这是一个最小的streamlit应用")

st.header("静态数据展示")
st.metric(label="总记录数",value=1280)
st.metric(label="今日新增",value=37)

df=pd.DataFrame({
    '时间': ['2026-05-20 10:00:01', '2026-05-20 10:00:02', '2026-05-20 10:00:03'],
    '数值': [42, 87, 13]
})

st.subheader("最近数据")
st.dataframe(df)

st.line_chart(df.set_index('时间')['数值'])