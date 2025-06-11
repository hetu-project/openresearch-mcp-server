#!/bin/bash

echo "Stopping OpenResearch MCP Server..."

# Find and stop process
PID=$(pgrep -f "python.*src/main.py")

if [ -n "$PID" ]; then
    echo "Found server process with PID: $PID"
    
    # Send TERM signal
    kill -TERM $PID
    
    # Wait for process to end
    sleep 2
    
    # Check if process is still running
    if kill -0 $PID 2>/dev/null; then
        echo "Process still running, force killing..."
        kill -KILL $PID
    fi
    
    echo "Server stopped successfully"
else
    echo "No running server found"
fi