#!/bin/bash

# Smart Scheduler Runner
# Usage: ./run.sh [ui|api|test|clean]

CMD=${1:-ui}

if [ "$CMD" == "ui" ]; then
    echo "🚀 Starting Streamlit UI..."
    streamlit run src/app_scheduler.py
elif [ "$CMD" == "api" ]; then
    echo "🔌 Starting API Server..."
    python3 src/api_scheduler.py
elif [ "$CMD" == "test" ]; then
    echo "🧪 Running Tests..."
    # Example test runner
    python3 tests/debug_constraints.py
elif [ "$CMD" == "clean" ]; then
    echo "🧹 Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} +
    rm -f *.log
else
    echo "Unknown command: $CMD"
    echo "Usage: ./run.sh [ui|api|test|clean]"
fi
