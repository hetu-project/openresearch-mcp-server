#!/usr/bin/env python3
"""
Interactive MCP Server Test
Interactive Test MCP Server - Fixed Version
"""

import asyncio
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import TextContent

class InteractiveTest:
    def __init__(self):
        self.server: AcademicMCPServer | None = None
    
    async def setup(self):
        """Initialize server"""
        print("🚀 Initializing MCP Server...")
        
        try:
            self.server = AcademicMCPServer()
            await self.server.initialize()
            print("✅ Server initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize server: {e}")
            raise
        
    async def show_menu(self):
        """Display menu"""
        print("\n" + "=" * 50)
        print("🧪 OpenResearch MCP Server Interactive Test")
        print("=" * 50)
        print("1. List all tools")
        print("2. Search papers")
        print("3. Search authors") 
        print("4. Get author papers")
        print("5. Get paper details")
        print("6. Get paper citations")  # New
        print("7. Get trending papers")
        print("8. Get top keywords")
        print("9. Server health check")
        print("10. Server info")
        print("0. Exit")
        print("-" * 50)
    
    async def list_tools(self):
        """List all tools"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📋 Available Tools:")
        
        try:
            # Directly access tool definitions
            tools = self.server.tool_definitions
            
            for i, tool in enumerate(tools, 1):
                print(f"{i:2d}. {tool.name}")
                print(f"     {tool.description}")
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
    
    def _extract_text_from_content(self, content_list) -> str:
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
    
    async def _call_tool_directly(self, tool_name: str, arguments: dict) -> list[TextContent]:
        """Directly call tool function"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if tool_name not in self.server.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Directly call tool function
        result = await self.server.tools[tool_name](arguments)
        
        # Ensure return TextContent list
        if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
            return result
        elif isinstance(result, list):
            return [TextContent(type="text", text=str(item)) for item in result]
        else:
            return [TextContent(type="text", text=str(result))]
    
    async def search_papers(self):
        """Search papers"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        query = input("\n🔍 Enter search query: ").strip()
        if not query:
            print("❌ Query cannot be empty")
            return
        
        limit = input("Enter limit (default 5): ").strip()
        limit = int(limit) if limit.isdigit() else 5
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n🔍 Searching for: '{query}' (limit: {limit}, format: {return_format})")
        
        try:
            result = await self._call_tool_directly(
                "search_papers",
                {
                    "query": query,
                    "limit": limit,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
            
            # Ask if want to get details
            if return_format == "markdown":
                get_details = input("\n🔍 Would you like to get details for any paper? (y/n): ").strip().lower()
                if get_details == 'y':
                    title = input("Enter the complete or partial paper title: ").strip()
                    if title:
                        await self._get_paper_details_by_title(title)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def search_authors(self):
        """Search authors"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        query = input("\n👥 Enter author name: ").strip()
        if not query:
            print("❌ Author name cannot be empty")
            return
        
        limit = input("Enter limit (default 3): ").strip()
        limit = int(limit) if limit.isdigit() else 3
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n👥 Searching for author: '{query}' (limit: {limit}, format: {return_format})")
        
        try:
            result = await self._call_tool_directly(
                "search_authors",
                {
                    "query": query,
                    "limit": limit,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # async def get_author_details(self):
    #     """Get author details"""
    #     if not self.server:
    #         print("❌ Server not initialized")
    #         return
            
    #     print("\n👤 Get Author Details")
    #     print("You can enter multiple author IDs separated by commas")
    #     print("Example: bb72631c-aae9-43a8-a48c-c9ee7c6e6768")
        
    #     author_ids_input = input("\n📝 Enter author ID(s): ").strip()
    #     if not author_ids_input:
    #         print("❌ Author ID cannot be empty")
    #         return
        
    #     # Handle multiple IDs (comma-separated)
    #     author_ids = [id.strip() for id in author_ids_input.split(',') if id.strip()]
        
    #     if not author_ids:
    #         print("❌ No valid author IDs provided")
    #         return
        
    #     # Choose return format
    #     print("\nChoose return format:")
    #     print("1. Markdown (formatted display)")
    #     print("2. JSON (raw data)")
    #     format_choice = input("Enter choice (1 or 2, default 1): ").strip()
    #     return_format = "json" if format_choice == "2" else "markdown"
        
    #     print(f"\n👤 Getting details for author(s): {', '.join(author_ids)}")
    #     print(f"Format: {return_format}")
        
    #     try:
    #         result = await self._call_tool_directly(
    #             "get_author_details",
    #             {
    #                 "author_ids": author_ids,
    #                 "format": return_format
    #             }
    #         )
            
    #         print("\n✅ Results:")
    #         text_result = self._extract_text_from_content(result)
    #         print(text_result)
                
    #     except Exception as e:
    #         print(f"❌ Error: {e}")
    
    async def get_author_papers(self):
        """Get author papers"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📄 Get Author Papers")
        print("Enter the author's UUID to get their published papers")
        print("Example: bb72631c-aae9-43a8-a48c-c9ee7c6e6768")
        
        author_id = input("\n📝 Enter author ID (UUID): ").strip()
        if not author_id:
            print("❌ Author ID cannot be empty")
            return
        
        # Get limit
        limit = input("Enter limit (default 20): ").strip()
        limit = int(limit) if limit.isdigit() else 20
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n📄 Getting papers for author: {author_id}")
        print(f"Limit: {limit}, Format: {return_format}")
        
        try:
            result = await self._call_tool_directly(
                "get_author_papers",
                {
                    "author_id": author_id,
                    "limit": limit,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def get_paper_details(self):
        """Get paper details"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📄 Get Paper Details")
        print("Enter paper title(s) to get detailed information")
        print("Examples:")
        print("  Single: WakeMint: Detecting Sleepminting Vulnerabilities in NFT Smart Contracts")
        print("  Multiple: title1,title2,title3 (comma-separated)")
        print("  Partial: WakeMint (partial title also works)")
        
        titles_input = input("\n📝 Enter paper title(s): ").strip()
        if not titles_input:
            print("❌ Paper title(s) cannot be empty")
            return
        
        # Parse input titles
        titles = [title.strip() for title in titles_input.split(',') if title.strip()]
        
        if not titles:
            print("❌ No valid titles provided")
            return
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n📄 Getting details for {len(titles)} paper(s)")
        print(f"Titles: {', '.join([t[:50] + '...' if len(t) > 50 else t for t in titles])}")
        print(f"Format: {return_format}")
        
        try:
            result = await self._call_tool_directly(
                "get_paper_details",
                {
                    "titles": titles,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _get_paper_details_by_title(self, title: str):
        """Helper method to get paper details by title"""
        try:
            result = await self._call_tool_directly(
                "get_paper_details",
                {
                    "titles": [title],
                    "format": "markdown"
                }
            )
            
            print("\n📄 Paper Details:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
            
        except Exception as e:
            print(f"❌ Error getting details: {e}")
    
    async def get_paper_citations(self):
        """Get paper citations"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📊 Get Paper Citations")
        print("Enter paper ID (UUID) to get citation relationships")
        print("Example: 39807969-21a4-4ea6-b4bb-3ec08a1d162a")
        
        paper_id = input("\n📝 Enter paper ID: ").strip()
        if not paper_id:
            print("❌ Paper ID cannot be empty")
            return
        
        # Validate UUID format
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, paper_id.lower()):
            print("❌ Invalid UUID format")
            print("💡 Tip: Use 'Search papers' to find paper IDs")
            return
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n📊 Getting citations for paper: {paper_id}")
        print(f"Format: {return_format}")
        
        try:
            result = await self._call_tool_directly(
                "get_paper_citations",
                {
                    "paper_id": paper_id,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
                
        except Exception as e:
            print(f"❌ Error getting citations: {e}")
    
    async def get_trending_papers(self):
        """Get trending papers"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n📈 Get Trending Papers")
        print("Time windows: week, month, year")
        time_window = input("Enter time window (default: month): ").strip()
        if time_window not in ["week", "month", "year"]:
            time_window = "month"
        
        limit = input("Enter limit (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        # 选择返回格式
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n📈 Getting trending papers ({time_window}, limit: {limit}, format: {return_format})")
        
        try:
            result = await self._call_tool_directly(
                "get_trending_papers",
                {
                    "time_window": time_window,
                    "limit": limit,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
            # If it's Markdown format, ask if user wants to view paper details
            if return_format == "markdown":
                view_details = input("\n🔍 Would you like to view details of any paper? (y/n): ").strip().lower()
                if view_details == 'y':
                    paper_id = input("Enter paper ID: ").strip()
                    if paper_id:
                        print(f"\n📄 Getting details for paper: {paper_id}")
                        try:
                            detail_result = await self._call_tool_directly(
                                "get_paper_details",
                                {
                                    "paper_ids": [paper_id],
                                    "format": "markdown"
                                }
                            )
                            detail_text = self._extract_text_from_content(detail_result)
                            print("\n📄 Paper Details:")
                            print(detail_text)
                        except Exception as e:
                            print(f"❌ Error getting paper details: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

    
    async def get_top_keywords(self):
        """Get top keywords"""
        if not self.server:
            print("❌ Server not initialized")
            return
            
        print("\n🏷️ Get Top Keywords")
        limit = input("Enter limit (default 20): ").strip()
        limit = int(limit) if limit.isdigit() else 20
        
        # Choose return format
        print("\nChoose return format:")
        print("1. Markdown (formatted display)")
        print("2. JSON (raw data)")
        format_choice = input("Enter choice (1 or 2, default 1): ").strip()
        return_format = "json" if format_choice == "2" else "markdown"
        
        print(f"\n🏷️ Getting top keywords (limit: {limit}, format: {return_format})")
        
        try:
            result = await self._call_tool_directly(
                "get_top_keywords",
                {
                    "limit": limit,
                    "format": return_format
                }
            )
            
            print("\n✅ Results:")
            text_result = self._extract_text_from_content(result)
            print(text_result)
            
            # If it's Markdown format, ask if user wants to search papers with a keyword
            if return_format == "markdown":
                search_papers = input("\n🔍 Would you like to search papers with any keyword? (y/n): ").strip().lower()
                if search_papers == 'y':
                    keyword = input("Enter keyword: ").strip()
                    if keyword:
                        print(f"\n📄 Searching papers with keyword: {keyword}")
                        try:
                            search_result = await self._call_tool_directly(
                                "search_papers",
                                {
                                    "query": keyword,
                                    "limit": 5,
                                    "format": "markdown"
                                }
                            )
                            search_text = self._extract_text_from_content(search_result)
                            print("\n📄 Related Papers:")
                            print(search_text)
                        except Exception as e:
                            print(f"❌ Error searching papers: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

    
    async def server_health_check(self):
        """Server health check"""
        if not self.server:
            print("❌ Server not initialized")
            return
        
        print("\n🏥 Checking server health...")
        
        try:
            # Check basic status
            print("✅ Basic Health Check:")
            print(f"Go Client: {'✅ Connected' if self.server.go_client else '❌ Not connected'}")
            print(f"Data Processor: {'✅ Ready' if self.server.data_processor else '❌ Not ready'}")
            print(f"Tools Loaded: {len(self.server.tools)}")
            print(f"Tool Definitions: {len(self.server.tool_definitions)}")
            
            # Test Go service connection
            if self.server.go_client:
                try:
                    async with self.server.go_client:
                        health_result = await self.server.go_client.health_check()
                        print(f"Go Service: ✅ {health_result.get('status', 'healthy')}")
                except Exception as e:
                    print(f"Go Service: ❌ {str(e)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def server_info(self):
        """Get server information"""
        if not self.server:
            print("❌ Server not initialized")
            return
        
        print("\n📊 Server Information:")
        
        try:
            print(f"Server Name: {self.server.server.name}")
            print(f"Available Tools: {len(self.server.tools)}")
            print(f"Tool Names: {', '.join(self.server.tools.keys())}")
            
            # Display tool categories
            print("\nTool Categories:")
            author_tools = [name for name in self.server.tools.keys() if 'author' in name]
            paper_tools = [name for name in self.server.tools.keys() if 'paper' in name]
            network_tools = [name for name in self.server.tools.keys() if 'network' in name]
            trend_tools = [name for name in self.server.tools.keys() if any(word in name for word in ['trend', 'keyword', 'top'])]
            
            if author_tools:
                print(f"  📚 Author Tools: {', '.join(author_tools)}")
            if paper_tools:
                print(f"  📄 Paper Tools: {', '.join(paper_tools)}")
            if network_tools:
                print(f"  🕸️  Network Tools: {', '.join(network_tools)}")
            if trend_tools:
                print(f"  📈 Trend Tools: {', '.join(trend_tools)}")
            
            # Display configuration information
            if hasattr(self.server, 'go_client') and self.server.go_client:
                print(f"\nGo Service URL: {self.server.go_client.base_url}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def run_quick_test(self):
        """Run quick test"""
        print("\n🚀 Running Quick Test...")
        
        try:
            # Test paper search
            print("\n1. Testing paper search...")
            result = await self._call_tool_directly(
                "search_papers",
                {
                    "query": "blockchain",
                    "limit": 2,
                    "format": "markdown"
                }
            )
            print("✅ Paper search: OK")
            
            # Test author search
            print("\n2. Testing author search...")
            result = await self._call_tool_directly(
                "search_authors",
                {
                    "query": "Zhang",
                    "limit": 2,
                    "format": "markdown"
                }
            )
            print("✅ Author search: OK")
            
            # Test top keywords
            print("\n3. Testing top keywords...")
            result = await self._call_tool_directly(
                "get_top_keywords",
                {
                    "limit": 5,
                    "format": "markdown"
                }
            )
            print("✅ Top keywords: OK")
            
            print("\n🎉 All quick tests passed!")
            
        except Exception as e:
            print(f"❌ Quick test failed: {e}")
    
    async def run_demo(self):
        """Run demo"""
        print("\n🎭 Running Demo...")
        
        try:
            # Demo paper search
            print("\n📄 Demo: Searching for 'Web3' papers...")
            result = await self._call_tool_directly(
                "search_papers",
                {
                    "query": "Web3",
                    "limit": 3,
                    "format": "markdown"
                }
            )
            text_result = self._extract_text_from_content(result)
            print(text_result[:500] + "..." if len(text_result) > 500 else text_result)
            
            # Demo top keywords
            print("\n🏷️ Demo: Top 10 keywords...")
            result = await self._call_tool_directly(
                "get_top_keywords",
                {
                    "limit": 10,
                    "format": "markdown"
                }
            )
            text_result = self._extract_text_from_content(result)
            print(text_result[:300] + "..." if len(text_result) > 300 else text_result)
            
            print("\n🎉 Demo completed!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    async def show_advanced_menu(self):
        """Show advanced menu"""
        print("\n" + "=" * 50)
        print("🔧 Advanced Options")
        print("=" * 50)
        print("1. Run quick test")
        print("2. Run demo")
        print("3. Test specific tool")
        print("4. Batch operations")
        print("5. Back to main menu")
        print("-" * 50)
    
    async def test_specific_tool(self):
        """Test specific tool"""
        if not self.server:
            print("❌ Server not initialized")
            return
        
        print("\n🔧 Test Specific Tool")
        print("Available tools:")
        
        tools = list(self.server.tools.keys())
        for i, tool_name in enumerate(tools, 1):
            print(f"{i:2d}. {tool_name}")
        
        try:
            choice = input("\nEnter tool number: ").strip()
            tool_index = int(choice) - 1
            
            if 0 <= tool_index < len(tools):
                tool_name = tools[tool_index]
                print(f"\n🔧 Testing tool: {tool_name}")
                
                # Provide default parameters based on tool type
                if "search_papers" in tool_name:
                    args = {"query": "test", "limit": 2, "format": "markdown"}
                elif "search_authors" in tool_name:
                    args = {"query": "test", "limit": 2, "format": "markdown"}
                elif "get_top_keywords" in tool_name:
                    args = {"limit": 5, "format": "markdown"}
                elif "get_trending_papers" in tool_name:
                    args = {"time_window": "month", "limit": 3, "format": "markdown"}
                else:
                    print("❌ No default parameters for this tool")
                    return
                
                result = await self._call_tool_directly(tool_name, args)
                text_result = self._extract_text_from_content(result)
                print("\n✅ Result:")
                print(text_result[:500] + "..." if len(text_result) > 500 else text_result)
            else:
                print("❌ Invalid tool number")
                
        except (ValueError, IndexError):
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def batch_operations(self):
        """Batch operations"""
        print("\n📦 Batch Operations")
        print("1. Batch search papers")
        print("2. Batch get paper details")
        print("3. Back to main menu")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            await self._batch_search_papers()
        elif choice == "2":
            await self._batch_get_paper_details()
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")
    
    async def _batch_search_papers(self):
        """Batch search papers"""
        print("\n🔍 Batch Search Papers")
        queries_input = input("Enter search queries (comma-separated): ").strip()
        
        if not queries_input:
            print("❌ No queries provided")
            return
        
        queries = [q.strip() for q in queries_input.split(',') if q.strip()]
        limit = input("Enter limit per query (default 3): ").strip()
        limit = int(limit) if limit.isdigit() else 3
        
        print(f"\n🔍 Searching {len(queries)} queries with limit {limit} each...")
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Query {i}/{len(queries)}: '{query}' ---")
            try:
                result = await self._call_tool_directly(
                    "search_papers",
                    {
                        "query": query,
                        "limit": limit,
                        "format": "markdown"
                    }
                )
                text_result = self._extract_text_from_content(result)
                print(text_result[:300] + "..." if len(text_result) > 300 else text_result)
            except Exception as e:
                print(f"❌ Error for query '{query}': {e}")
    
    async def _batch_get_paper_details(self):
        """Batch get paper details"""
        print("\n📄 Batch Get Paper Details")
        titles_input = input("Enter paper titles (comma-separated): ").strip()
        
        if not titles_input:
            print("❌ No titles provided")
            return
        
        titles = [t.strip() for t in titles_input.split(',') if t.strip()]
        
        print(f"\n📄 Getting details for {len(titles)} papers...")
        
        try:
            result = await self._call_tool_directly(
                "get_paper_details",
                {
                    "titles": titles,
                    "format": "markdown"
                }
            )
            text_result = self._extract_text_from_content(result)
            print("\n✅ Results:")
            print(text_result)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def run(self):
        """Run interactive test"""
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
                        await self.get_author_papers()
                    elif choice == "5":
                        await self.get_paper_details()
                    elif choice == "6":
                        await self.get_paper_citations()
                    elif choice == "7":
                        await self.get_trending_papers()
                    elif choice == "8":
                        await self.get_top_keywords()
                    elif choice == "9":
                        await self.server_health_check()
                    elif choice == "10":
                        await self.server_info()
                    elif choice == "99":  # Hidden advanced options
                        while True:
                            await self.show_advanced_menu()
                            adv_choice = input("Enter choice: ").strip()
                            if adv_choice == "1":
                                await self.run_quick_test()
                            elif adv_choice == "2":
                                await self.run_demo()
                            elif adv_choice == "3":
                                await self.test_specific_tool()
                            elif adv_choice == "4":
                                await self.batch_operations()
                            elif adv_choice == "5":
                                break
                            else:
                                print("❌ Invalid choice")
                            input("\nPress Enter to continue...")
                    else:
                        print("❌ Invalid choice")
                        print("💡 Tip: Enter '99' for advanced options")
                    
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
    """主函数"""
    print("🧪 OpenResearch MCP Server Interactive Test")
    print("=" * 50)
    
    test = InteractiveTest()
    await test.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

