#!/usr/bin/env python3
"""
Simple MCP Server Test Script
Test the basic functions of OpenResearch MCP Server - Fixed Version
"""

import asyncio
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import TextContent


def extract_text_from_content(content_list) -> str:
    """Safely extract text from content list"""
    text_parts = []
    for content in content_list:
        if isinstance(content, TextContent):
            text_parts.append(content.text)
        elif hasattr(content, 'text'):
            text_parts.append(content.text)
        else:
            # For non-text content, display type information
            text_parts.append(f"[{type(content).__name__}]")
    return "\n".join(text_parts)


async def call_tool_directly(server: AcademicMCPServer, tool_name: str, arguments: dict) -> list[TextContent]:
    """Directly call tool function"""
    if tool_name not in server.tools:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    # Directly call tool function
    result = await server.tools[tool_name](arguments)
    
    # Ensure return TextContent list
    if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
        return result
    elif isinstance(result, list):
        return [TextContent(type="text", text=str(item)) for item in result]
    else:
        return [TextContent(type="text", text=str(result))]


async def test_server_basic():
    """Test server basic functions"""
    print("🚀 Testing MCP Server Basic Functions...")
    
    server = AcademicMCPServer()
    await server.initialize()
    
    print("✅ Server created successfully")
    return server


async def test_list_tools(server: AcademicMCPServer):
    """Test tool list"""
    print("\n📋 Testing list_tools...")
    
    try:
        # Directly access tool definitions
        tools = server.tool_definitions
        
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Verify tool registry
        print(f"✅ Tool registry has {len(server.tools)} callable tools:")
        for tool_name in server.tools.keys():
            print(f"   - {tool_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return False


async def test_search_papers(server: AcademicMCPServer):
    """Test paper search"""
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
            # Display first 200 characters as preview
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
    """Test author search"""
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
            # Display first 200 characters as preview
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
    """Test trending papers"""
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
            # Display first 200 characters as preview
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
    """Test top keywords"""
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
            # Display first 200 characters as preview
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
    """Test server components"""
    print("\n🔧 Testing server components...")
    
    try:
        # Test basic components
        print("✅ Component Status:")
        print(f"   Go Client: {'✅ Ready' if server.go_client else '❌ Not ready'}")
        print(f"   Data Processor: {'✅ Ready' if server.data_processor else '❌ Not ready'}")
        print(f"   Tools Loaded: {len(server.tools)}")
        print(f"   Tool Definitions: {len(server.tool_definitions)}")
        
        # Test Go service connection
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
    """Test tool error handling"""
    print("\n⚠️ Testing error handling...")
    
    try:
        # Test nonexistent tool
        try:
            await call_tool_directly(server, "nonexistent_tool", {})
            print("❌ Should have raised error for nonexistent tool")
            return False
        except ValueError as e:
            print(f"✅ Correctly handled nonexistent tool: {str(e)[:50]}...")
        
        # Test invalid parameters
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
    """Main test function"""
    print("🧪 OpenResearch MCP Server Test Suite - Direct Testing")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    server = None
    
    try:
        # 1. Test server creation
        server = await test_server_basic()
        total_tests += 1
        tests_passed += 1
        
        # 2. Test tool list
        total_tests += 1
        if await test_list_tools(server):
            tests_passed += 1
        
        # 3. Test server components
        total_tests += 1
        if await test_server_components(server):
            tests_passed += 1
        
        # 4. Test paper search
        total_tests += 1
        if await test_search_papers(server):
            tests_passed += 1
        
        # 5. Test author search
        total_tests += 1
        if await test_search_authors(server):
            tests_passed += 1
        
        # 6. Test trending papers
        total_tests += 1
        if await test_get_trending_papers(server):
            tests_passed += 1
        
        # 7. Test top keywords
        total_tests += 1
        if await test_get_top_keywords(server):
            tests_passed += 1
        
        # 8. Test error handling
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
    
    # Output test results
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