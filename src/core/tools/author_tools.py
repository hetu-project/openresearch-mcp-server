from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class AuthorTools(BaseTools):
    """Author related tools - Support JSON format return"""
    
    def get_tools(self) -> List[Tool]:
        """Get tool definitions"""
        return [
            Tool(
                name="search_authors",
                description="Search academic authors, support filtering by name, institution, research field, etc.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query, supports author name"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter conditions",
                            "properties": {
                                "affiliation": {"type": "string", "description": "Institution name"},
                                "research_area": {"type": "string", "description": "Research field"}
                            }
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "Number of results to return"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown(formatted display) or json(raw data)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_author_papers",
                description="Get list of papers published by the author",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "Author ID"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "Number of results to return"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown(formatted display) or json(raw data)"
                        }
                    },
                    "required": ["author_id"]
                }
            )
        ]

    
    @handle_tool_error
    async def get_author_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get author papers tool - Support JSON format"""
        author_id = arguments["author_id"]
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "json")
        
        logger.info("Getting author papers", author_id=author_id, limit=limit, format=return_format)
        
        try:
            raw_result = await self.go_client.get_author_papers(author_id)
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_author_papers(raw_result, author_id, limit)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get author papers failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get Author Papers")
            return [TextContent(type="text", text=error_content)]
    
    
    def _format_author_papers(self, raw_result: Dict[str, Any], author_id: str, limit: int) -> str:
        """Format author papers"""
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        content = f"# 📄 Author Published Papers\n\n"
        content += f"**Author ID**: `{author_id}`\n"
        content += f"**Total Papers**: {count}\n"
        content += f"**Displayed**: {len(papers)}\n\n"
        
        if not papers:
            content += "❌ No papers found for this author.\n"
            return content
        
        content += f"## 📋 Paper List\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            paper_id = self._safe_get_str(paper, 'id')
            if paper_id:
                content += f"**Paper ID**: `{paper_id}`\n"
            
            published_at = self._safe_get_str(paper, 'published_at')
            if published_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                    content += f"**Published Date**: {formatted_date}\n"
                except:
                    content += f"**Published Date**: {published_at}\n"
            
            author_order = self._safe_get_int(paper, 'author_order')
            if author_order > 0:
                if author_order == 1:
                    order_text = "First Author"
                elif author_order == 2:
                    order_text = "Second Author"
                elif author_order == 3:
                    order_text = "Third Author"
                else:
                    order_text = f"{author_order}th Author"
                content += f"**Author Order**: {order_text}\n"
            
            is_corresponding = paper.get('is_corresponding')
            if is_corresponding:
                content += f"**Corresponding Author**: ✅ Yes\n"
            else:
                content += f"**Corresponding Author**: ❌ No\n"
            
            content += "\n---\n\n"
        
        if count > len(papers):
            content += f"💡 **Note**: Author has {count} papers in total, showing first {len(papers)}.\n\n"
        
        first_author_count = sum(1 for p in papers if p.get('author_order') == 1)
        corresponding_count = sum(1 for p in papers if p.get('is_corresponding'))
        
        content += f"## 📊 Statistics\n\n"
        content += f"- **First Author Papers**: {first_author_count}\n"
        content += f"- **Corresponding Author Papers**: {corresponding_count}\n"
        
        year_stats = {}
        for paper in papers:
            published_at = paper.get('published_at', '')
            if published_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    year = dt.year
                    year_stats[year] = year_stats.get(year, 0) + 1
                except:
                    pass
        
        if year_stats:
            content += f"- **Distribution by Year**:\n"
            for year in sorted(year_stats.keys(), reverse=True):
                content += f"  - {year}: {year_stats[year]} papers\n"
        
        return content


    @handle_tool_error
    async def search_authors(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Search authors tool - Support name and ID search"""
        query = arguments.get("query")
        author_id = arguments.get("author_id")
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "json")

        if not query and not author_id:
            return [TextContent(type="text", text="❌ Please provide search criteria (name or ID)")]

        logger.info("Searching authors IN AUTHOR TOOL", query=query, author_id=author_id, filters=filters, format=return_format)
        
        try:
            raw_result = await self.go_client.search_authors(
                query=query,
                author_id=author_id,
                filters=filters,
                limit=limit
            )
            
            if return_format == "json":
                json_str = json.dumps(raw_result, ensure_ascii=False, indent=2)
                logger.debug("Returning JSON format", json_data=json_str)
                return [TextContent(type="text", text=json_str)]
            else:
                if query:
                    search_term = str(query)
                elif author_id:
                    search_term = f"ID: {str(author_id)}"
                else:
                    search_term = "Unknown search criteria"
                
                content = self._format_authors_result(raw_result, search_term)
                logger.debug("Returning Markdown format", markdown_content=content)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            error_content = self._format_error_response(str(e), "Author Search")
            return [TextContent(type="text", text=error_content)]

    def _format_authors_result(self, raw_result: Dict[str, Any], search_term: str) -> str:
        """Unified author result formatting method"""
        authors = raw_result.get("authors", [])
        count = raw_result.get("count", len(authors))
        
        if not authors:
            return self._format_empty_result(search_term, "author")
        
        if len(authors) == 1:
            return self._format_single_author_details(authors[0], search_term)
        else:
            return self._format_multiple_authors_list(authors, count, search_term)

    def _format_single_author_details(self, author: Dict[str, Any], search_term: str) -> str:
        """Format single author details"""
        content = f"# 👤 Author Details\n\n"
        content += f"**Search Criteria**: {search_term}\n\n"
        
        content += f"## Basic Information\n"
        content += f"**Name**: {self._safe_get_str(author, 'name', 'Unknown')}\n"
        content += f"**ID**: `{self._safe_get_str(author, 'id', 'N/A')}`\n"
        content += f"**Affiliation**: {self._safe_get_str(author, 'affiliation', 'N/A')}\n"
        
        email = self._safe_get_str(author, 'email')
        if email:
            content += f"**Email**: {email}\n"
        
        content += f"\n## 📊 Academic Metrics\n"
        content += f"**Paper Count**: {self._safe_get_int(author, 'paper_count')}\n"
        content += f"**Citation Count**: {self._safe_get_int(author, 'citation_count')}\n"
        content += f"**H-index**: {self._safe_get_int(author, 'h_index')}\n"
        
        interests = author.get('research_interests')
        if interests:
            content += f"\n## 🔬 Research Interests\n"
            if isinstance(interests, list):
                content += f"{', '.join(interests)}\n"
            else:
                content += f"{interests}\n"
        
        coauthors = author.get('coauthors', [])
        if coauthors:
            content += f"\n## 🤝 Collaboration Network ({len(coauthors)} co-authors)\n\n"
            
            sorted_coauthors = sorted(
                coauthors, 
                key=lambda x: self._safe_get_int(x, 'collaboration_count'), 
                reverse=True
            )
            
            for i, coauthor in enumerate(sorted_coauthors[:10], 1):
                collab_count = self._safe_get_int(coauthor, 'collaboration_count')
                coauthor_name = self._safe_get_str(coauthor, 'name', 'Unknown')
                coauthor_id = self._safe_get_str(coauthor, 'id', 'N/A')
                
                content += f"{i:2d}. **{coauthor_name}** - {collab_count} collaborations\n"
                content += f"     ID: `{coauthor_id}`\n"
                
                affiliation = self._safe_get_str(coauthor, 'affiliation')
                if affiliation:
                    content += f"     Affiliation: {affiliation}\n"
                content += "\n"
            
            if len(coauthors) > 10:
                content += f"... and {len(coauthors) - 10} more co-authors\n"
        
        return content

    def _format_multiple_authors_list(self, authors: List[Dict[str, Any]], count: int, search_term: str) -> str:
        """Format multiple authors list information"""
        content = self._format_list_header("Author Search Results", count, search_term)
        
        for i, author in enumerate(authors, 1):
            name = self._safe_get_str(author, 'name', 'Unknown Author')
            content += f"## {i}. {name}\n\n"
            
            content += self._format_author_basic_info(author)
            
            interests = author.get('research_interests')
            if interests:
                if isinstance(interests, list):
                    content += f"**Research Interests**: {', '.join(interests)}\n"
                else:
                    content += f"**Research Interests**: {interests}\n"
            
            email = self._safe_get_str(author, 'email')
            if email:
                content += f"**Email**: {email}\n"
            
            coauthors = author.get('coauthors', [])
            if coauthors:
                content += f"**Co-authors**: {len(coauthors)}"
                top_coauthors = sorted(coauthors, key=lambda x: self._safe_get_int(x, 'collaboration_count'), reverse=True)[:3]
                if top_coauthors:
                    names = [self._safe_get_str(c, 'name') for c in top_coauthors if self._safe_get_str(c, 'name')]
                    if names:
                        content += f" (Main: {', '.join(names)})"
                content += "\n"
            
            content += f"**ID**: `{self._safe_get_str(author, 'id', 'N/A')}`\n"
            content += "\n---\n\n"
        
        return content