#!/bin/bash

echo "Stopping OpenResearch MCP Server..."

# 查找并停止进程
PID=$(pgrep -f "python.*src/main.py")

if [ -n "$PID" ]; then
    echo "Found server process with PID: $PID"
    
    # 发送 TERM 信号
    kill -TERM $PID
    
    # 等待进程结束
    sleep 2
    
    # 检查进程是否还在运行
    if kill -0 $PID 2>/dev/null; then
        echo "Process still running, force killing..."
        kill -KILL $PID
    fi
    
    echo "Server stopped successfully"
else
    echo "No running server found"
fi
