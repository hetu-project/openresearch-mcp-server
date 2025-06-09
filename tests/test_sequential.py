import subprocess
import json
import time
import sys

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
        
        # 读取多行输出直到找到JSON-RPC响应
        print("Reading init responses...")
        for i in range(10):  # 最多读10行
            line = process.stdout.readline()
            if not line:
                break
            print(f"Line {i+1}: {line.strip()}")
            
            # 检查是否是JSON-RPC响应
            try:
                data = json.loads(line.strip())
                if data.get("jsonrpc") == "2.0" and data.get("id") == 1:
                    print(f"Found init response: {data}")
                    break
            except json.JSONDecodeError:
                continue
        
        # 等待一下
        time.sleep(0.5)
        
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
        
        print("\nSending tool request...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # 读取工具响应
        print("Reading tool responses...")
        for i in range(10):  # 最多读10行
            line = process.stdout.readline()
            if not line:
                break
            print(f"Tool Line {i+1}: {line.strip()}")
            
            # 检查是否是JSON-RPC响应
            try:
                data = json.loads(line.strip())
                if data.get("jsonrpc") == "2.0" and data.get("id") == 2:
                    print(f"Found tool response: {data}")
                    break
            except json.JSONDecodeError:
                continue
        
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