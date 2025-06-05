#!/usr/bin/env python3
"""
Interactive MCP Server Test
交互式测试 MCP Server
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import ListToolsRequest, CallToolRequest, CallToolRequestParams, TextContent

class InteractiveTest:
    def __init__(self):
        self.server: AcademicMCPServer | None = None
    
    async def setup(self):
        """初始化服务器"""
        print("🚀 Initializing MCP Server...")
        
        try:
            self.server = AcademicMCPServer()
            await self.server.initialize()
            print("✅ Server initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize server: {e}")
            raise
    
    async def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 50)
        print("🧪 OpenResearch MCP Server Interactive Test")
        print("=" * 50)
        print("1. List all tools")
        print("2. Search papers")
        print("3. Search authors") 
        print("4. Get trending papers")
        print("5. Get top keywords")
        print("0. Exit")
        print("-" * 50)
    
    async def list_tools(self):
        """列出所有工具"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📋 Available Tools:")
        
        try:
            request = ListToolsRequest(
                method="tools/list"
            )
            result = await self.server.list_tools(request)
            
            for i, tool in enumerate(result.tools, 1):
                print(f"{i:2d}. {tool.name}")
                print(f"     {tool.description}")
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
    
    def _extract_text_from_content(self, content_list) -> str:
        """安全地从内容列表中提取文本"""
        text_parts = []
        for content in content_list:
            if isinstance(content, TextContent):
                text_parts.append(content.text)
            elif hasattr(content, 'text'):
                text_parts.append(content.text)
            else:
                # 对于非文本内容，显示类型信息
                text_parts.append(f"[{type(content).__name__}]")
        return "\n".join(text_parts)
    
    async def search_papers(self):
        """搜索论文"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        query = input("\n🔍 Enter search query: ").strip()
        if not query:
            print("❌ Query cannot be empty")
            return
        
        limit = input("Enter limit (default 5): ").strip()
        limit = int(limit) if limit.isdigit() else 5
        
        print(f"\n🔍 Searching for: '{query}' (limit: {limit})")
        
        try:
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="search_papers",
                    arguments={
                        "query": query,
                        "limit": limit
                    }
                )
            )
            
            result = await self.server.call_tool(request)
            
            if result.content and not result.isError:
                print("\n✅ Results:")
                text_result = self._extract_text_from_content(result.content)
                print(text_result)
            else:
                error_msg = "Unknown error"
                if result.content:
                    error_msg = self._extract_text_from_content(result.content)
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def search_authors(self):
        """搜索作者"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        query = input("\n👥 Enter author name: ").strip()
        if not query:
            print("❌ Author name cannot be empty")
            return
        
        limit = input("Enter limit (default 3): ").strip()
        limit = int(limit) if limit.isdigit() else 3
        
        print(f"\n👥 Searching for author: '{query}' (limit: {limit})")
        
        try:
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="search_authors",
                    arguments={
                        "query": query,
                        "limit": limit
                    }
                )
            )
            
            result = await self.server.call_tool(request)
            
            if result.content and not result.isError:
                print("\n✅ Results:")
                text_result = self._extract_text_from_content(result.content)
                print(text_result)
            else:
                error_msg = "Unknown error"
                if result.content:
                    error_msg = self._extract_text_from_content(result.content)
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def get_trending_papers(self):
        """获取热门论文"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📈 Time windows: week, month, year")
        time_window = input("Enter time window (default: month): ").strip()
        if time_window not in ["week", "month", "year"]:
            time_window = "month"
        
        limit = input("Enter limit (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        print(f"\n📈 Getting trending papers ({time_window}, limit: {limit})")
        
        try:
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_trending_papers",
                    arguments={
                        "time_window": time_window,
                        "limit": limit
                    }
                )
            )
            
            result = await self.server.call_tool(request)
            
            if result.content and not result.isError:
                print("\n✅ Results:")
                text_result = self._extract_text_from_content(result.content)
                print(text_result)
            else:
                error_msg = "Unknown error"
                if result.content:
                    error_msg = self._extract_text_from_content(result.content)
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def get_top_keywords(self):
        """获取热门关键词"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        limit = input("\n🏷️ Enter limit (default 20): ").strip()
        limit = int(limit) if limit.isdigit() else 20
        
        print(f"\n🏷️ Getting top keywords (limit: {limit})")
        
        try:
            request = CallToolRequest(
                method="tools/call",
                params=CallToolRequestParams(
                    name="get_top_keywords",
                    arguments={
                        "limit": limit
                    }
                )
            )
            
            result = await self.server.call_tool(request)
            
            if result.content and not result.isError:
                print("\n✅ Results:")
                text_result = self._extract_text_from_content(result.content)
                print(text_result)
            else:
                error_msg = "Unknown error"
                if result.content:
                    error_msg = self._extract_text_from_content(result.content)
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def run(self):
        """运行交互式测试"""
        try:
            await self.setup()
            
            while True:
                await self.show_menu()
                
                try:
                    choice = input("Enter your choice: ").strip()
                    
                    if choice == "0":
                        print("👋 Goodbye!")
                        break
                    elif choice == "1":
                        await self.list_tools()
                    elif choice == "2":
                        await self.search_papers()
                    elif choice == "3":
                        await self.search_authors()
                    elif choice == "4":
                        await self.get_trending_papers()
                    elif choice == "5":
                        await self.get_top_keywords()
                    else:
                        print("❌ Invalid choice")
                    
                    input("\nPress Enter to continue...")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    input("\nPress Enter to continue...")
        
        finally:
            # 清理资源
            if self.server:
                await self.server.cleanup()

async def main():
    test = InteractiveTest()
    await test.run()

if __name__ == "__main__":
    asyncio.run(main())
