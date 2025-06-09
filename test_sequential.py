import subprocess
import json
import time

def test_sequential():
    command = ["./venv/bin/python", "src/main.py"]
    
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        print("Sending init request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取初始化响应
        init_response = process.stdout.readline()
        print(f"Init response: {init_response.strip()}")
        
        # 等待一下
        time.sleep(0.2)
        
        # 发送工具调用请求
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_papers",
                "arguments": {"query": "machine learning", "limit": 3}
            }
        }
        
        print("Sending tool request...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # 读取工具响应
        tool_response = process.stdout.readline()
        print(f"Tool response: {tool_response.strip()}")
        
        # 关闭输入
        process.stdin.close()
        
        # 等待进程结束
        process.wait(timeout=10)
        
    except Exception as e:
        print(f"Error: {e}")
        if process.poll() is None:
            process.kill()
    finally:
        if process.poll() is None:
            process.terminate()

if __name__ == "__main__":
    test_sequential()
