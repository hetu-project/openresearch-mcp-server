#!/usr/bin/env python3
"""
Simple MCP Server Test Script
测试 OpenResearch MCP Server 的基本功能 - 修正版本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import TextContent


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


async def call_tool_directly(server: AcademicMCPServer, tool_name: str, arguments: dict) -> list[TextContent]:
    """直接调用工具函数"""
    if tool_name not in server.tools:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    # 直接调用工具函数
    result = await server.tools[tool_name](arguments)
    
    # 确保返回 TextContent 列表
    if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
        return result
    elif isinstance(result, list):
        return [TextContent(type="text", text=str(item)) for item in result]
    else:
        return [TextContent(type="text", text=str(result))]


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
        # 直接访问工具定义
        tools = server.tool_definitions
        
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # 验证工具注册表
        print(f"✅ Tool registry has {len(server.tools)} callable tools:")
        for tool_name in server.tools.keys():
            print(f"   - {tool_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return False


async def test_search_papers(server: AcademicMCPServer):
    """测试论文搜索"""
    print("\n🔍 Testing search_papers...")
    
    try:
        result = await call_tool_directly(
            server,
            "search_papers",
            {
                "query": "machine learning",
                "limit": 5
            }
        )
        
        if result:
            print("✅ Search papers successful")
            text_result = extract_text_from_content(result)
            print(f"   Result length: {len(text_result)} characters")
            # 显示前200个字符作为预览
            preview = text_result[:200] + "..." if len(text_result) > 200 else text_result
            print(f"   Preview: {preview}")
        else:
            print("❌ Search papers returned empty result")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error searching papers: {e}")
        return False


async def test_search_authors(server: AcademicMCPServer):
    """测试作者搜索"""
    print("\n👥 Testing search_authors...")
    
    try:
        result = await call_tool_directly(
            server,
            "search_authors",
            {
                "query": "Zhang Wei",
                "limit": 3
            }
        )
        
        if result:
            print("✅ Search authors successful")
            text_result = extract_text_from_content(result)
            print(f"   Result length: {len(text_result)} characters")
            # 显示前200个字符作为预览
            preview = text_result[:200] + "..." if len(text_result) > 200 else text_result
            print(f"   Preview: {preview}")
        else:
            print("❌ Search authors returned empty result") 
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error searching authors: {e}")
        return False


async def test_get_trending_papers(server: AcademicMCPServer):
    """测试热门论文"""
    print("\n📈 Testing get_trending_papers...")
    
    try:
        result = await call_tool_directly(
            server,
            "get_trending_papers",
            {
                "time_window": "month",
                "limit": 5
            }
        )
        
        if result:
            print("✅ Get trending papers successful")
            text_result = extract_text_from_content(result)
            print(f"   Result length: {len(text_result)} characters")
            # 显示前200个字符作为预览
            preview = text_result[:200] + "..." if len(text_result) > 200 else text_result
            print(f"   Preview: {preview}")
        else:
            print("❌ Get trending papers returned empty result")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error getting trending papers: {e}")
        return False


async def test_get_top_keywords(server: AcademicMCPServer):
    """测试热门关键词"""
    print("\n🏷️ Testing get_top_keywords...")
    
    try:
        result = await call_tool_directly(
            server,
            "get_top_keywords",
            {
                "limit": 10
            }
        )
        
        if result:
            print("✅ Get top keywords successful")
            text_result = extract_text_from_content(result)
            print(f"   Result length: {len(text_result)} characters")
            # 显示前200个字符作为预览
            preview = text_result[:200] + "..." if len(text_result) > 200 else text_result
            print(f"   Preview: {preview}")
        else:
            print("❌ Get top keywords returned empty result")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error getting top keywords: {e}")
        return False


async def test_server_components(server: AcademicMCPServer):
    """测试服务器组件"""
    print("\n🔧 Testing server components...")
    
    try:
        # 测试基本组件
        print("✅ Component Status:")
        print(f"   Go Client: {'✅ Ready' if server.go_client else '❌ Not ready'}")
        print(f"   Data Processor: {'✅ Ready' if server.data_processor else '❌ Not ready'}")
        print(f"   Tools Loaded: {len(server.tools)}")
        print(f"   Tool Definitions: {len(server.tool_definitions)}")
        
        # 测试 Go 服务连接
        if server.go_client:
            try:
                async with server.go_client:
                    health_result = await server.go_client.health_check()
                    print(f"   Go Service Health: ✅ {health_result.get('status', 'healthy')}")
            except Exception as e:
                print(f"   Go Service Health: ❌ {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing components: {e}")
        return False


async def test_tool_error_handling(server: AcademicMCPServer):
    """测试工具错误处理"""
    print("\n⚠️ Testing error handling...")
    
    try:
        # 测试不存在的工具
        try:
            await call_tool_directly(server, "nonexistent_tool", {})
            print("❌ Should have raised error for nonexistent tool")
            return False
        except ValueError as e:
            print(f"✅ Correctly handled nonexistent tool: {str(e)[:50]}...")
        
        # 测试无效参数
        try:
            await call_tool_directly(server, "search_papers", {"invalid_param": "test"})
            print("✅ Tool handled invalid parameters gracefully")
        except Exception as e:
            print(f"✅ Tool correctly rejected invalid parameters: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        return False


async def main():
    """主测试函数"""
    print("🧪 OpenResearch MCP Server Test Suite - Direct Testing")
    print("=" * 60)
    
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
        
        # 3. 测试服务器组件
        total_tests += 1
        if await test_server_components(server):
            tests_passed += 1
        
        # 4. 测试论文搜索
        total_tests += 1
        if await test_search_papers(server):
            tests_passed += 1
        
        # 5. 测试作者搜索
        total_tests += 1
        if await test_search_authors(server):
            tests_passed += 1
        
        # 6. 测试热门论文
        total_tests += 1
        if await test_get_trending_papers(server):
            tests_passed += 1
        
        # 7. 测试热门关键词
        total_tests += 1
        if await test_get_top_keywords(server):
            tests_passed += 1
        
        # 8. 测试错误处理
        total_tests += 1
        if await test_tool_error_handling(server):
            tests_passed += 1
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if server:
            await server.cleanup()
    
    # 输出测试结果
    print("\n" + "=" * 60)
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
