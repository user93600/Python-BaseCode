# ============================================
# Integrated Platform - One-Click Launcher
# Usage: .\start_all.ps1
# ============================================

$EMQX_BIN = "C:\Users\33762\Downloads\emqx-5.3.2-windows-amd64\bin\emqx.cmd"
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Integrated Platform Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ========== 1. EMQX ==========
Write-Host "[1/3] EMQX MQTT Broker" -ForegroundColor Yellow
$emqxRunning = & $EMQX_BIN ping 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] EMQX is already running" -ForegroundColor Green
} else {
    Write-Host "  [..] Starting EMQX..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$EMQX_BIN`" start" -WindowStyle Minimized
    Start-Sleep -Seconds 5
    Write-Host "  [OK] EMQX started" -ForegroundColor Green
}
Write-Host "  MQTT:1883  |  WS:8083  |  Dashboard: http://127.0.0.1:18083" -ForegroundColor Gray

# ========== 2. MySQL ==========
Write-Host "[2/3] MySQL Database" -ForegroundColor Yellow
Write-Host "  [!!] Make sure MySQL is running and database tcp_data_db exists" -ForegroundColor DarkYellow

# ========== 3. Streamlit ==========
Write-Host "[3/3] Starting Streamlit..." -ForegroundColor Yellow
Write-Host "  --> http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================" -ForegroundColor DarkGray
Write-Host "  Ctrl+C to stop Streamlit" -ForegroundColor Gray
Write-Host "  emqx stop  to stop EMQX" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor DarkGray
Write-Host ""

# Open browser
Start-Process "http://localhost:8501"

# Launch Streamlit (blocking, Ctrl+C to stop)
Set-Location $PROJECT_ROOT
streamlit run practice08/integrated_platform.py
