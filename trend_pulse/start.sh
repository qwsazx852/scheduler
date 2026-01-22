#!/bin/bash
cd "$(dirname "$0")"

# 當腳本結束時 (Ctrl+C)，殺死所有子程序 (包含後端)
trap "kill 0" EXIT

echo "========================================"
echo "🔥 TrendPulse 快速啟動腳本"
echo "========================================"

# --- 1. 檢查並啟動後端 ---
echo "Checking Backend..."
cd backend

# 檢查是否需要安裝 Python 依賴 (簡單檢查)
# 為了速度，這裡假設如果有 requirements.txt 且執行失敗才安裝，或者每次都 quiet install
if ! python3 -c "import fastapi; import uvicorn" 2>/dev/null; then
    echo "📦 安裝/更新 Python 依賴..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Python 依賴安裝失敗，請檢查 backend/requirements.txt"
        exit 1
    fi
fi

echo "🚀 啟動後端伺服器 (Port 8001)..."
# 啟動後端於背景
python3 main.py &
BACKEND_PID=$!

# 等待後端啟動 (簡單 sleep，或者是用迴圈檢查 port)
sleep 2

cd ..

# --- 2. 檢查並啟動前端 ---
echo "Checking Frontend..."

if [ ! -d "node_modules" ]; then
    echo "📦 偵測到初次執行，正在安裝前端依賴 (npm install)..."
    npm install
fi

echo "🚀 啟動前端介面 (Port 5173)..."

# 自動開啟瀏覽器
(sleep 3 && open "http://localhost:5173") &

# 啟動 Vite
npm run dev
