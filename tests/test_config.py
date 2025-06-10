
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings

def test_config():
    print("=== 配置信息 ===")
    print(f"服务器名称: {settings.server_name}")
    print(f"服务器版本: {settings.server_version}")
    print(f"调试模式: {settings.debug}")
    print(f"Go服务地址: {settings.go_service_url}")
    print(f"日志级别: {settings.log_level}")
    print(f"最大结果数: {settings.max_results}")

if __name__ == "__main__":
    test_config()
