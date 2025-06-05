#!/usr/bin/env python3
"""
Simple MCP Server Test Script
测试 OpenResearch MCP Server 的基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import ListToolsRequest, CallToolRequest, CallToolRequestParams, TextContent


def extract_text_from_content(content_list) -> str:
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


async def test_server_basic():
    """测试服务器基本功能"""
    print("🚀 Testing MCP Server Basic Functions...")
    
    server = AcademicMCPServer()
    await server.initialize()
    
    print("✅ Server created successfully")
    return server

async def test_list_tools(server: AcademicMCPServer):
    """测试工具列表"""
    print("\n📋 Testing list_tools...")
    
    try:
        request = ListToolsRequest(
            method="tools/list"
        )
        result = await server.list_tools(request)
        
        print(f"✅ Found {len(result.tools)} tools:")
        for tool in result.tools:
            print(f"   - {tool.name}: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return False

async def test_search_papers(server: AcademicMCPServer):
    """测试论文搜索"""
    print("\n🔍 Testing search_papers...")
    
    try:
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="search_papers",
                arguments={
                    "query": "machine learning",
                    "limit": 5
                }
            )
        )
        
        result = await server.call_tool(request)
        
        if result.content and not result.isError:
            print("✅ Search papers successful")
            text_result = extract_text_from_content(result.content)
            print(f"   Result length: {len(text_result)} characters")
        else:
            error_msg = "Unknown error"
            if result.content:
                error_msg = extract_text_from_content(result.content)
            print(f"❌ Search papers failed: {error_msg}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error searching papers: {e}")
        return False

async def test_search_authors(server: AcademicMCPServer):
    """测试作者搜索"""
    print("\n👥 Testing search_authors...")
    
    try:
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="search_authors",
                arguments={
                    "query": "Zhang Wei",
                    "limit": 3
                }
            )
        )
        
        result = await server.call_tool(request)
        
        if result.content and not result.isError:
            print("✅ Search authors successful")
            text_result = extract_text_from_content(result.content)
            print(f"   Result length: {len(text_result)} characters")
        else:
            error_msg = "Unknown error"
            if result.content:
                error_msg = extract_text_from_content(result.content)
            print(f"❌ Search authors failed: {error_msg}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error searching authors: {e}")
        return False

async def test_get_trending_papers(server: AcademicMCPServer):
    """测试热门论文"""
    print("\n📈 Testing get_trending_papers...")
    
    try:
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="get_trending_papers",
                arguments={
                    "time_window": "month",
                    "limit": 5
                }
            )
        )
        
        result = await server.call_tool(request)
        
        if result.content and not result.isError:
            print("✅ Get trending papers successful")
            text_result = extract_text_from_content(result.content)
            print(f"   Result length: {len(text_result)} characters")
        else:
            error_msg = "Unknown error"
            if result.content:
                error_msg = extract_text_from_content(result.content)
            print(f"❌ Get trending papers failed: {error_msg}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error getting trending papers: {e}")
        return False

async def test_get_top_keywords(server: AcademicMCPServer):
    """测试热门关键词"""
    print("\n🏷️ Testing get_top_keywords...")
    
    try:
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="get_top_keywords",
                arguments={
                    "limit": 10
                }
            )
        )
        
        result = await server.call_tool(request)
        
        if result.content and not result.isError:
            print("✅ Get top keywords successful")
            text_result = extract_text_from_content(result.content)
            print(f"   Result length: {len(text_result)} characters")
        else:
            error_msg = "Unknown error"
            if result.content:
                error_msg = extract_text_from_content(result.content)
            print(f"❌ Get top keywords failed: {error_msg}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error getting top keywords: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 OpenResearch MCP Server Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    server = None
    
    try:
        # 1. 测试服务器创建
        server = await test_server_basic()
        total_tests += 1
        tests_passed += 1
        
        # 2. 测试工具列表
        total_tests += 1
        if await test_list_tools(server):
            tests_passed += 1
        
        # 3. 测试论文搜索
        total_tests += 1
        if await test_search_papers(server):
            tests_passed += 1
        
        # 4. 测试作者搜索
        total_tests += 1
        if await test_search_authors(server):
            tests_passed += 1
        
        # 5. 测试热门论文
        total_tests += 1
        if await test_get_trending_papers(server):
            tests_passed += 1
        
        # 6. 测试热门关键词
        total_tests += 1
        if await test_get_top_keywords(server):
            tests_passed += 1
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
    finally:
        if server:
            await server.cleanup()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)