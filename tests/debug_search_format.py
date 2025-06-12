#!/usr/bin/env python3
"""
Debug search paper return format
"""
import asyncio
import sys
import json
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server import AcademicMCPServer
from mcp.types import TextContent

async def debug_search_format():
    """Debug search papers return format"""
    server = None
    
    try:
        print("🔍 Debugging search_papers return format...")
        
        # Initialize server
        server = AcademicMCPServer()
        await server.initialize()
        
        # Directly call search tool
        if "search_papers" in server.tools:
            print("\n📋 Calling search_papers tool...")
            
            result = await server.tools["search_papers"]({
                "query": "web3",
                "limit": 3
            })
            
            print(f"\n🔍 Raw result analysis:")
            print(f"   Type: {type(result)}")
            print(f"   Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            if isinstance(result, list):
                print(f"   List contents:")
                for i, item in enumerate(result):
                    print(f"     [{i}] Type: {type(item)}")
                    
                    if isinstance(item, TextContent):
                        print(f"         TextContent.type: {item.type}")
                        print(f"         TextContent.text length: {len(item.text)}")
                        print(f"         TextContent.text preview: {item.text[:200]}...")
                        
                        # Try to parse as JSON
                        try:
                            parsed_json = json.loads(item.text)
                            print(f"         ✅ Content is valid JSON")
                            print(f"         JSON keys: {list(parsed_json.keys()) if isinstance(parsed_json, dict) else 'Not a dict'}")
                            
                            # If it's paper search results
                            if isinstance(parsed_json, dict) and "papers" in parsed_json:
                                papers = parsed_json["papers"]
                                print(f"         📄 Found {len(papers)} papers")
                                if papers:
                                    first_paper = papers[0]
                                    print(f"         First paper keys: {list(first_paper.keys())}")
                                    if "title" in first_paper:
                                        print(f"         First paper title: {first_paper['title'][:100]}...")
                                        
                        except json.JSONDecodeError:
                            print(f"         ❌ Content is not valid JSON")
                            print(f"         Raw text: {item.text[:500]}...")
                    
                    elif hasattr(item, 'text'):
                        print(f"         Has text attribute: {item.text[:200]}...")
                    else:
                        print(f"         Raw content: {str(item)[:200]}...")
            
            # Test _extract_text_from_content method
            print(f"\n🔧 Testing _extract_text_from_content:")
            
            # Simulate method from interactive_test.py
            def extract_text_from_content(content_list) -> str:
                text_parts = []
                for content in content_list:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif hasattr(content, 'text'):
                        text_parts.append(content.text)
                    else:
                        text_parts.append(f"[{type(content).__name__}]")
                return "\n".join(text_parts)
            
            extracted_text = extract_text_from_content(result)
            print(f"   Extracted text length: {len(extracted_text)}")
            print(f"   Extracted text preview: {extracted_text[:300]}...")
            
            # Try to parse extracted text as JSON
            try:
                parsed_extracted = json.loads(extracted_text)
                print(f"   ✅ Extracted text is valid JSON")
                print(f"   JSON structure: {type(parsed_extracted)}")
                if isinstance(parsed_extracted, dict):
                    print(f"   JSON keys: {list(parsed_extracted.keys())}")
            except json.JSONDecodeError:
                print(f"   ❌ Extracted text is not valid JSON")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if server:
            await server.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_search_format())