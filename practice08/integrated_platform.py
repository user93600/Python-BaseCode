"""
集成学习任务平台
单文件整合：文件操作 / TCP数据监控 / MQTT消息 / 数据查询 / 数据看板
streamlit run integrated_platform.py
"""

# ============================================================
# 区块 A：导入 + 全局配置
# ============================================================
import streamlit as st
import pandas as pd
import pymysql
import socket
import threading
import time
import os
import csv
import io
import json
from datetime import datetime
from collections import deque

# --- streamlit-autorefresh ---
from streamlit_autorefresh import st_autorefresh

# --- MQTT ---
import paho.mqtt.client as mqtt

# --- Flask (后台线程) ---
from flask import Flask, jsonify, request

# --- 模块级常量 ---
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "data/number"
TCP_HOST = "0.0.0.0"
TCP_PORT = 8888
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

# --- 模块级共享状态（跨 Streamlit 重跑持久化） ---
if "tcp_data_deque" not in st.session_state:
    st.session_state.tcp_data_deque = deque(maxlen=20)
if "tcp_data_lock" not in st.session_state:
    st.session_state.tcp_data_lock = threading.Lock()
if "mqtt_msg_deque" not in st.session_state:
    st.session_state.mqtt_msg_deque = deque(maxlen=200)
if "mqtt_msg_lock" not in st.session_state:
    st.session_state.mqtt_msg_lock = threading.Lock()

# 服务启停标志 (用 services_state dict，daemon 线程读取)
if "services_state" not in st.session_state:
    st.session_state.services_state = {"tcp": False, "flask": False, "mqtt_listener": False}

# 模块级 DB 密码（从 session_state 恢复，供后台线程使用）
_DB_PASSWORD = st.session_state.get("pwd", "")

# 诊断日志（显示在 Sidebar，方便排查问题）
if "debug_log" not in st.session_state:
    st.session_state.debug_log = deque(maxlen=50)
debug_log = st.session_state.debug_log

# 便捷引用（后续代码直接使用）
tcp_data_deque = st.session_state.tcp_data_deque
tcp_data_lock = st.session_state.tcp_data_lock
mqtt_msg_deque = st.session_state.mqtt_msg_deque
mqtt_msg_lock = st.session_state.mqtt_msg_lock
services_state = st.session_state.services_state


# ============================================================
# 区块 B：数据库辅助函数
# ============================================================
def get_db_connection():
    """使用模块级密码创建 MySQL 连接（线程安全）"""
    return pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=_DB_PASSWORD,
        database="tcp_data_db",
        charset="utf8mb4",
    )


def save_to_database(client_ip, data):
    """插入一条 TCP 记录"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO tcp_record (client_ip, receive_data) VALUES (%s, %s)"
        cursor.execute(sql, (client_ip, data))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn:
            conn.close()


def query_by_timerange(start_str, end_str):
    """按时间段查询记录"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
        SELECT id, client_ip, receive_data, create_time
        FROM tcp_record
        WHERE create_time >= %s AND create_time <= %s
        ORDER BY create_time
    """
    cursor.execute(sql, (start_str, end_str))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # 转换 datetime 为字符串，方便 JSON 序列化
    for row in rows:
        if isinstance(row.get("create_time"), datetime):
            row["create_time"] = row["create_time"].strftime("%Y-%m-%d %H:%M:%S")
    return rows


def query_latest(n=20):
    """查询最近 N 条记录"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT receive_data, create_time FROM tcp_record ORDER BY id DESC LIMIT %s", (n,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    rows.reverse()
    for row in rows:
        if isinstance(row.get("create_time"), datetime):
            row["create_time"] = row["create_time"].strftime("%Y-%m-%d %H:%M:%S")
    return rows


def query_last_hour_df():
    """加载最近1小时数据为 DataFrame"""
    conn = get_db_connection()
    query = """
        SELECT receive_data, create_time
        FROM tcp_record
        WHERE create_time >= NOW() - INTERVAL 1 HOUR
        ORDER BY create_time
    """
    df = pd.read_sql(query, conn)
    conn.close()
    if not df.empty:
        df["receive_data"] = pd.to_numeric(df["receive_data"], errors="coerce")
        df["create_time"] = pd.to_datetime(df["create_time"])
        df = df.dropna(subset=["receive_data"])
    return df


# ============================================================
# 区块 C：后台服务线程
# ============================================================

# --- TCP Server ---
def handle_client(client_socket, client_addr, mqtt_pub: mqtt.Client):
    """处理单个 TCP 客户端"""
    client_ip = client_addr[0]
    debug_log.append(f"[TCP] 客户端已连接: {client_ip}:{client_addr[1]}")
    reader = client_socket.makefile("r", encoding="utf-8")
    try:
        while services_state["tcp"]:
            line = reader.readline()
            if not line:
                debug_log.append(f"[TCP] 客户端断开: {client_ip}")
                break
            try:
                num = int(line.strip())
            except ValueError:
                continue

            # 写入共享 deque → UI 实时图表
            with tcp_data_lock:
                tcp_data_deque.append(num)

            # 保存到 MySQL
            db_ok = save_to_database(client_ip, str(num))
            if not db_ok:
                debug_log.append(f"[DB] 保存失败: {num}")

            # MQTT 广播
            try:
                mqtt_pub.publish(MQTT_TOPIC, str(num))
            except Exception as e:
                debug_log.append(f"[MQTT] 发布失败: {e}")
    except Exception as e:
        debug_log.append(f"[TCP] handle_client 异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client_socket.close()


def tcp_server_thread():
    """TCP 服务端：多线程 accept，持久运行直到 services_state["tcp"]=False"""
    import traceback
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(5)
        server_socket.settimeout(1.0)  # 允许定期检查退出标志
        debug_log.append(f"[TCP] 服务端已在 {TCP_HOST}:{TCP_PORT} 启动")
    except Exception as e:
        debug_log.append(f"[TCP] 启动失败: {e}")
        traceback.print_exc()
        services_state["tcp"] = False
        return

    mqtt_pub = mqtt.Client()
    try:
        mqtt_pub.connect(MQTT_BROKER, MQTT_PORT, 60)
        debug_log.append(f"[MQTT] 发布者已连接 {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        debug_log.append(f"[MQTT] 发布者连接失败: {e}")
    mqtt_pub.loop_start()

    while services_state["tcp"]:
        try:
            client_sock, client_addr = server_socket.accept()
            debug_log.append(f"[TCP] 新连接: {client_addr}")
            t = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr, mqtt_pub),
                daemon=True,
            )
            t.start()
        except socket.timeout:
            continue
        except Exception as e:
            debug_log.append(f"[TCP] accept 异常: {e}")
            break

    debug_log.append("[TCP] 服务端已停止")
    mqtt_pub.loop_stop()
    try:
        mqtt_pub.disconnect()
    except Exception:
        pass
    server_socket.close()


# --- Flask API ---
def create_flask_app():
    """工厂函数：创建 Flask app（在线程中运行）"""
    app = Flask(__name__)

    @app.route("/api/records")
    def get_records():
        start = request.args.get("start", "2020-01-01 00:00:00")
        end = request.args.get("end", "2099-12-31 23:59:59")

        for time_str in (start, end):
            try:
                datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return (
                    jsonify({"error": f"时间格式错误 {time_str}，请使用 YYYY-MM-DD HH:MM:SS"}),
                    400,
                )

        if start > end:
            return jsonify({"error": "起始时间不能晚于结束时间"}), 400

        data = query_by_timerange(start, end)
        return jsonify(data)

    @app.route("/api/latest")
    def latest():
        rows = query_latest(20)
        return jsonify(rows)

    return app


def flask_thread():
    """运行 Flask API"""
    app = create_flask_app()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)


# --- MQTT Listener ---
def mqtt_listener_thread():
    """订阅 MQTT 主题，消息写入共享 deque"""

    def on_connect(client, userdata, flags, rc):
        client.subscribe(MQTT_TOPIC)
        debug_log.append(f"[MQTT] 监听已订阅: {MQTT_TOPIC}")

    def on_message(client, userdata, msg):
        with mqtt_msg_lock:
            mqtt_msg_deque.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "topic": msg.topic,
                    "payload": msg.payload.decode(errors="replace"),
                }
            )

    sub = mqtt.Client()
    sub.on_connect = on_connect
    sub.on_message = on_message
    try:
        sub.connect(MQTT_BROKER, MQTT_PORT, 60)
        debug_log.append(f"[MQTT] 监听已连接 {MQTT_BROKER}:{MQTT_PORT}")
    except ConnectionRefusedError:
        debug_log.append("[MQTT] 监听连接失败: broker 未运行")
        services_state["mqtt_listener"] = False
        return
    except Exception as e:
        debug_log.append(f"[MQTT] 监听连接失败: {e}")
        services_state["mqtt_listener"] = False
        return
    sub.loop_forever()


# ============================================================
# 区块 D-1：文件操作工具函数（移植自 read_file.py）
# ============================================================
def get_file_info(folder_path):
    """扫描文件夹，返回文件信息列表"""
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                size = os.path.getsize(full_path)
                ctime_timestamp = os.path.getctime(full_path)
                ctime_str = datetime.fromtimestamp(ctime_timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                file_list.append(
                    {
                        "文件路径": full_path,
                        "文件名": file,
                        "文件大小(字节)": size,
                        "创建时间": ctime_str,
                    }
                )
            except Exception:
                pass
    return file_list


# ============================================================
# 区块 D-2：页面渲染函数
# ============================================================

# --- Page 1: 文件操作 ---
def render_page_file_ops():
    st.subheader("📁 文件操作")
    st.caption("扫描目标文件夹，列出所有文件信息并导出 CSV")

    folder_path = st.text_input(
        "目标文件夹路径",
        value=os.path.expanduser("~"),
        key="file_ops_path",
    )

    if st.button("开始扫描", key="btn_scan"):
        folder_path = folder_path.strip().strip('"').strip("'")
        if not os.path.isdir(folder_path):
            st.error("错误：输入的路径不是一个有效的文件夹！")
        else:
            with st.spinner(f"正在扫描 {folder_path} ..."):
                file_list = get_file_info(folder_path)
            st.success(f"共找到 {len(file_list)} 个文件")

            if file_list:
                df = pd.DataFrame(file_list)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # CSV 下载按钮
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                st.download_button(
                    label="📥 导出 CSV",
                    data=csv_buffer.getvalue(),
                    file_name="file_info.csv",
                    mime="text/csv",
                    key="btn_download_csv",
                )
            else:
                st.info("没有找到任何文件，未生成 CSV。")


# --- Page 2: TCP 数据监控 ---
def render_page_tcp_monitor():
    st.subheader("📡 TCP 数据监控")
    st.caption("实时显示 TCP 客户端发来的随机数（最近 20 个数据点）")

    # 每秒自动刷新
    st_autorefresh(interval=1000, limit=None, key="tcp_refresh")

    with tcp_data_lock:
        data = list(tcp_data_deque)

    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("最新数据", data[-1])
        col2.metric("均值", round(sum(data) / len(data), 2))
        col3.metric("数据点数", len(data))

        chart_df = pd.DataFrame({"index": range(len(data)), "随机数值": data})
        st.line_chart(chart_df, x="index", y="随机数值", height=350)
    else:
        st.info("⏳ 等待 TCP 客户端发送数据...")
        st.caption("请确保已启动 TCP 服务，并在另一个终端运行 client_step2.py")


# --- Page 3: MQTT 消息 ---
def render_page_mqtt():
    st.subheader("📨 MQTT 消息日志")
    st.caption("实时显示 MQTT 主题上的消息（最新 200 条）")

    st_autorefresh(interval=1000, limit=None, key="mqtt_refresh")

    with mqtt_msg_lock:
        messages = list(mqtt_msg_deque)

    if messages:
        # 倒序显示：最新在上
        lines = []
        for m in reversed(messages):
            lines.append(f"[{m['time']}]  {m['topic']}  →  {m['payload']}")
        log_text = "\n".join(lines)
        st.code(log_text, language="text")
        st.caption(f"共 {len(messages)} 条消息")
    else:
        st.info("⏳ 等待 MQTT 消息...")
        st.caption("请确保 MQTT Broker 正在运行，且 TCP 服务有数据发布")


# --- Page 4: 数据查询 ---
def render_page_query():
    st.subheader("🔍 数据查询")
    st.caption("按时间段查询 MySQL 中的历史记录，同时提供 RESTful API 示例")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("开始日期", key="start_date")
        start_time = st.time_input("开始时间", key="start_time")
    with col2:
        end_date = st.date_input("结束日期", key="end_date")
        end_time = st.time_input("结束时间", key="end_time")

    if st.button("🔎 查询", key="btn_query"):
        start_str = f"{start_date} {start_time}"
        end_str = f"{end_date} {end_time}"

        try:
            datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            st.error("时间格式错误，请重新选择")
            return

        if start_str > end_str:
            st.error("起始时间不能晚于结束时间")
            return

        with st.spinner("查询中..."):
            rows = query_by_timerange(start_str, end_str)

        if rows:
            st.success(f"共 {len(rows)} 条记录")
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("该时间段内没有数据")

    # RESTful API 说明
    with st.expander("🌐 RESTful API 调用示例"):
        st.markdown("Flask API 后台运行在 `http://127.0.0.1:5000`")
        st.code(
            '# 查询时间段数据\n'
            'curl "http://127.0.0.1:5000/api/records?start=2026-01-01%2000:00:00&end=2026-12-31%2023:59:59"\n\n'
            '# 查询最新 20 条\n'
            'curl "http://127.0.0.1:5000/api/latest"',
            language="bash",
        )


# --- Page 5: 数据看板 ---
def render_page_dashboard():
    st.subheader("📊 数据看板")
    st.caption("最近一小时的统计分析，每 3 秒自动刷新")

    st_autorefresh(interval=3000, limit=None, key="dashboard_refresh")

    df = query_last_hour_df()

    if df.empty:
        st.warning("⚠️ 最近 1 小时内没有数据，请确保 TCP 客户端正在发送数据")
        return

    # 指标卡片
    st.subheader("📈 实时统计")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("最新数据", int(df["receive_data"].iloc[-1]))
    col2.metric("平均值", round(df["receive_data"].mean(), 2))
    col3.metric("最大值", int(df["receive_data"].max()))
    col4.metric("最小值", int(df["receive_data"].min()))

    # 趋势折线图
    st.subheader("📉 最近一小时趋势")
    chart_data = df.set_index("create_time")["receive_data"]
    st.line_chart(chart_data)

    # 数值分布直方图
    st.subheader("📊 数值分布")
    try:
        hist_data = df["receive_data"].value_counts(bins=10).sort_index()
        st.bar_chart(hist_data)
    except Exception:
        st.caption("数据不足以生成分布图")

    # 最新记录
    st.subheader("📋 最新十条记录")
    st.dataframe(
        df.tail(10)[["create_time", "receive_data"]].sort_values(
            "create_time", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 区块 E：主入口
# ============================================================
def main():
    global _DB_PASSWORD

    st.set_page_config(
        page_title="集成学习任务平台",
        page_icon="🚀",
        layout="wide",
    )

    # ===== 登录门禁 =====
    if "is_login" not in st.session_state:
        st.session_state.is_login = False

    if not st.session_state.is_login:
        st.title("🔐 集成学习任务平台")
        st.caption("请使用 MySQL 密码登录")

        pwd_input = st.text_input("MySQL 密码", type="password", key="pwd_input")

        if st.button("登 录", key="btn_login"):
            try:
                test_conn = pymysql.connect(
                    host="127.0.0.1",
                    port=3306,
                    user="root",
                    database="tcp_data_db",
                    charset="utf8mb4",
                    password=pwd_input,
                )
                test_conn.close()
                st.session_state.is_login = True
                st.session_state.pwd = pwd_input
                _DB_PASSWORD = pwd_input
                st.rerun()
            except pymysql.err.OperationalError:
                st.error("❌ 密码错误或数据库不可达")
        st.stop()

    # 从 session_state 恢复密码到模块级变量（供后台线程使用）
    _DB_PASSWORD = st.session_state.get("pwd", "")

    # ===== 已登录：主界面 =====
    st.title("🚀 集成学习任务平台")

    # ----- Sidebar -----
    with st.sidebar:
        st.header("⚙️ 后台服务")

        # ---- TCP 服务 ----
        col_tcp_status, col_tcp_btn = st.columns([1, 2])
        with col_tcp_status:
            tcp_running = services_state["tcp"]
            st.markdown(
                f"**TCP** {'🟢' if tcp_running else '🔴'}**:**{TCP_PORT}"
            )
        with col_tcp_btn:
            if st.button(
                "停止 TCP" if tcp_running else "启动 TCP",
                key="btn_tcp",
                use_container_width=True,
            ):
                if not tcp_running:
                    services_state["tcp"] = True
                    t = threading.Thread(target=tcp_server_thread, daemon=True)
                    t.start()
                    st.session_state._tcp_t = t
                else:
                    services_state["tcp"] = False

        # ---- Flask API ----
        col_flask_status, col_flask_btn = st.columns([1, 2])
        with col_flask_status:
            flask_running = services_state["flask"]
            st.markdown(
                f"**API** {'🟢' if flask_running else '🔴'}**:**{FLASK_PORT}"
            )
        with col_flask_btn:
            if st.button(
                "停止 API" if flask_running else "启动 API",
                key="btn_flask",
                use_container_width=True,
            ):
                if not flask_running:
                    services_state["flask"] = True
                    t = threading.Thread(target=flask_thread, daemon=True)
                    t.start()
                    st.session_state._flask_t = t
                else:
                    services_state["flask"] = False

        # ---- MQTT 监听 ----
        col_mqtt_status, col_mqtt_btn = st.columns([1, 2])
        with col_mqtt_status:
            mqtt_running = services_state["mqtt_listener"]
            st.markdown(
                f"**MQTT** {'🟢' if mqtt_running else '🔴'}**:**{MQTT_TOPIC}"
            )
        with col_mqtt_btn:
            if st.button(
                "停止监听" if mqtt_running else "启动监听",
                key="btn_mqtt",
                use_container_width=True,
            ):
                if not mqtt_running:
                    services_state["mqtt_listener"] = True
                    t = threading.Thread(target=mqtt_listener_thread, daemon=True)
                    t.start()
                    st.session_state._mqtt_t = t
                else:
                    services_state["mqtt_listener"] = False

        st.divider()

        # ---- 诊断日志 ----
        with st.expander("🔧 诊断日志", expanded=False):
            if debug_log:
                lines = []
                for entry in reversed(debug_log):
                    lines.append(entry)
                st.code("\n".join(lines), language="text")
            else:
                st.caption("暂无日志")
            if st.button("清空日志", key="btn_clear_log"):
                debug_log.clear()

        st.divider()

        # ---- 页面导航 ----
        st.subheader("📂 导航")
        page_labels = {
            "file_ops": "📁 文件操作",
            "tcp_monitor": "📡 TCP 数据监控",
            "mqtt_msgs": "📨 MQTT 消息",
            "data_query": "🔍 数据查询",
            "dashboard": "📊 数据看板",
        }
        page = st.radio(
            "选择页面",
            options=list(page_labels.keys()),
            format_func=lambda k: page_labels[k],
            label_visibility="collapsed",
            key="nav_radio",
        )

    # ----- Page Routing -----
    if page == "file_ops":
        render_page_file_ops()
    elif page == "tcp_monitor":
        render_page_tcp_monitor()
    elif page == "mqtt_msgs":
        render_page_mqtt()
    elif page == "data_query":
        render_page_query()
    elif page == "dashboard":
        render_page_dashboard()


if __name__ == "__main__":
    main()
