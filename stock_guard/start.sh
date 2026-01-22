echo "🚀 正在啟動 StockGuard..."
cd "$(dirname "$0")"

# Start Backend in background
node server.cjs &
BACKEND_PID=$!

# Function to cleanup background process on exit
cleanup() {
    echo "🛑 Stopping Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID
}
trap cleanup EXIT

# Wait a moment for backend to initialize
sleep 2

# Open Browser
open http://localhost:5173

# Start Frontend
npm run dev
