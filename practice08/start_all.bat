@echo off
chcp 65001 >nul
title 集成学习任务平台 - 一键启动

set EMQX_PATH=C:\Users\33762\Downloads\emqx-5.3.2-windows-amd64\bin

echo.
echo ╔══════════════════════════════════════════╗
echo ║     🚀 集成学习任务平台 一键启动         ║
echo ╚══════════════════════════════════════════╝
echo.

:: ========== 1. 启动 EMQX ==========
echo [1/3] 检查 EMQX 状态...
"%EMQX_PATH%\emqx.cmd" ping >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ EMQX 已在运行
) else (
    echo   ⏳ 正在启动 EMQX...
    start "EMQX" "%EMQX_PATH%\emqx.cmd" start
    echo   ⏳ 等待 EMQX 就绪...
    timeout /t 5 /nobreak >nul
    echo   ✅ EMQX 已启动
)
echo   📡 MQTT 端口: 1883  |  WebSocket: 8083  |  控制台: http://127.0.0.1:18083
echo.

:: ========== 2. 提醒 MySQL ==========
echo [2/3] 请确保 MySQL 服务已启动！
echo   🗄️  需要数据库: tcp_data_db  (表: tcp_record)
echo.

:: ========== 3. 启动 Streamlit ==========
echo [3/3] 启动 Streamlit 平台...
echo   🌐 浏览器将打开: http://localhost:8501
echo.
echo ══════════════════════════════════════════
echo   按 Ctrl+C 可停止 Streamlit
echo   停止 EMQX: 在另一个终端执行 emqx stop
echo ══════════════════════════════════════════
echo.

cd /d "%~dp0..\"

start "" http://localhost:8501
streamlit run practice08/integrated_platform.py
