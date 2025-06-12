import asyncio
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings

def test_config():
    print("=== Configuration Info ===")
    print(f"Server Name: {settings.server_name}")
    print(f"Server Version: {settings.server_version}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Go Service URL: {settings.go_service_url}")
    print(f"Log Level: {settings.log_level}")
    print(f"Max Results: {settings.max_results}")

if __name__ == "__main__":
    test_config()
