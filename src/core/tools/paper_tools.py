from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class PaperTools(BaseTools):
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="search_papers",
                description="Search academic papers with filters like keywords, authors, time range",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query, supports paper title keywords"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter conditions",
                            "properties": {
                                "keywords": {"type": "string", "description": "Keywords"},
                                "author": {"type": "string", "description": "Author name"},
                                "year": {"type": "integer", "description": "Publication year"},
                                "venue": {"type": "string", "description": "Conference or journal name"},
                                "doi": {"type": "string", "description": "DOI"}
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
            name="get_paper_details",
            description="Get detailed information for a specific paper by title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Paper title, supports full or partial title"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "json"],
                        "default": "markdown",
                        "description": "Return format: markdown(formatted display) or json(raw data)"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="get_paper_citations",
                description="Get paper citation relationships",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_id": {
                            "type": "string",
                            "description": "Paper ID"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown(formatted display) or json(raw data)"
                        }
                    },
                    "required": ["paper_id"]
                }
            )
        ]
    
    @handle_tool_error
    async def search_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments["query"]
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "json")

        logger.info("Searching papers", query=query, filters=filters, format=return_format)
        
        try:
            raw_result = await self.go_client.search_papers(
                query=query,
                filters=filters,
                limit=limit
            )
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_search_result(raw_result, query)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            error_content = self._format_error_response(str(e), "Paper search")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_paper_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        title = arguments["title"]
        return_format = arguments.get("format", "json")
        
        logger.info("Getting paper details by title", title=title, format=return_format)
        
        try:
            all_papers = []
            raw_result = await self.go_client.get_paper_details(titles=[title], limit=2)
            if return_format == "json":
                json_text = json.dumps(raw_result, ensure_ascii=False, indent=2)
                logger.debug("Returning JSON result", json_content=json_text)
                logger.info("Paper details JSON result", 
                        paper_count=len(all_papers), 
                        json_length=len(json_text))
                logger.debug(f"Full JSON response:\n{json_text}")
                return [TextContent(type="text", text=json_text)]
            else:
                content = self._format_paper_details(raw_result)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get paper details")
            return [TextContent(type="text", text=error_content)]
    
    def _find_best_title_match(self, target_title: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        target_lower = target_title.lower().strip()
        
        if not papers:
            return {}
    
        for paper in papers:
            paper_title = paper.get('title', '').lower().strip()
            if paper_title == target_lower:
                return paper
        
        for paper in papers:
            paper_title = paper.get('title', '').lower().strip()
            if target_lower in paper_title or paper_title in target_lower:
                return paper
        
        return papers[0]

    @handle_tool_error
    async def get_paper_citations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        paper_id = arguments["paper_id"]
        return_format = arguments.get("format", "json")
        
        logger.info("Getting paper citations", paper_id=paper_id, format=return_format)
        
        try:
            raw_result = await self.go_client.get_paper_citations(paper_id)
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_citations(raw_result, paper_id)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper citations failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get paper citations")
            return [TextContent(type="text", text=error_content)]
    
    def _format_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        if not papers:
            return self._format_empty_result(query, "papers")
        
        content = self._format_list_header("Paper Search Results", count, query)
        content += f"## Paper List (Showing first {len(papers)})\n\n"
        
        for i, paper in enumerate(papers, 1):
            content += f"### {i}. {self._safe_get_str(paper, 'title', 'Unknown Title')}\n\n"
            
            content += self._format_paper_basic_info(paper)
            
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"**Abstract**: {self._truncate_text(abstract)}\n"
            
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"**Keywords**: {self._format_keywords(keywords)}\n"
            
            url = self._safe_get_str(paper, 'url')
            doi = self._safe_get_str(paper, 'doi')
            if url:
                content += f"**Link**: {url}\n"
            elif doi:
                content += f"**DOI**: {doi}\n"
            
            content += f"**ID**: {self._safe_get_str(paper, 'id', 'N/A')}\n"
            content += "\n---\n\n"
        
        return content
    
    def _format_paper_details(self, raw_result: Dict[str, Any]) -> str:
        papers = raw_result.get("papers", [])
        
        if not papers:
            return "❌ No paper details found."
        
        content = "# 📄 Paper Details\n\n"
        
        for paper in papers:
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"## {title}\n\n"
            
            content += "### 📋 Basic Information\n"
            content += f"**Paper ID**: `{self._safe_get_str(paper, 'id', 'N/A')}`\n"
            content += self._format_paper_basic_info(paper)
            
            authors = paper.get('authors', [])
            if authors:
                content += f"\n### 👥 Authors ({len(authors)})\n"
                for j, author in enumerate(authors, 1):
                    author_name = self._safe_get_str(author, 'name', 'Unknown')
                    author_id = self._safe_get_str(author, 'id')
                    content += f"{j}. **{author_name}**"
                    if author_id:
                        content += f" (ID: `{author_id}`)"
                    content += "\n"
            
            content += "\n### 📊 Impact Metrics\n"
            citations = self._safe_get_int(paper, 'citations')
            references_count = self._safe_get_int(paper, 'references_count')
            likes_count = self._safe_get_int(paper, 'likes_count')
            
            content += f"**Citations**: {citations}\n"
            content += f"**References**: {references_count}\n"
            content += f"**Likes**: {likes_count}\n"
            
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"\n**Keywords**: {self._format_keywords(keywords, max_count=10)}\n"
            
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"\n### 📝 Abstract\n{abstract}\n"
            
            content += "\n### 🔗 Links and Resources\n"
            content += self._format_paper_links(paper)
            
            img_url = self._safe_get_str(paper, 'img_url')
            if img_url:
                content += f"- [📸 Paper Preview]({img_url})\n"
            
            interaction_info = self._format_user_interaction(paper)
            if interaction_info.strip():
                content += f"\n### 👤 User Interaction\n{interaction_info}"
            
            content += "\n---\n\n"
        
        return content

    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        info = ""
        
        published_at = paper.get('published_at')
        if published_at:
            try:
                if isinstance(published_at, (int, float)):
                    from datetime import datetime
                    dt = datetime.fromtimestamp(published_at)
                    formatted_date = dt.strftime('%Y-%m-%d')
                else:
                    formatted_date = self._format_date(str(published_at))
                info += f"**Publication Date**: {formatted_date}\n"
            except:
                info += f"**Publication Date**: {published_at}\n"
        
        venue_name = self._safe_get_str(paper, 'venue_name')
        venue_id = self._safe_get_str(paper, 'venue_id')
        if venue_name:
            info += f"**Published in**: {venue_name}"
            if venue_id and venue_id != venue_name:
                info += f" ({venue_id})"
            info += "\n"
        elif venue_id:
            info += f"**Published in**: {venue_id}\n"
        
        return info

    def _format_paper_links(self, paper: Dict[str, Any]) -> str:
        links = []
        
        url = self._safe_get_str(paper, 'url')
        if url:
            if 'arxiv.org' in url:
                links.append(f"- [📄 arXiv Paper]({url})")
            elif 'ieee' in url.lower():
                links.append(f"- [📄 IEEE Paper]({url})")
            else:
                links.append(f"- [📄 Paper Link]({url})")
        
        doi = self._safe_get_str(paper, 'doi')
        if doi:
            if doi.startswith('10.'):
                doi_url = f"https://doi.org/{doi}"
                links.append(f"- [🔗 DOI]({doi_url}) (`{doi}`)")
            else:
                links.append(f"- **DOI**: `{doi}`")
        
        return "\n".join(links) + "\n" if links else ""

    def _format_user_interaction(self, paper: Dict[str, Any]) -> str:
        info = ""
        
        is_favorited = paper.get('is_favorited_by_user', False)
        is_liked = paper.get('is_liked_by_user', False)
        likes_count = self._safe_get_int(paper, 'likes_count')
        
        if is_favorited or is_liked or likes_count > 0:
            interaction_parts = []
            
            if is_favorited:
                interaction_parts.append("⭐ Favorited")
            
            if is_liked:
                interaction_parts.append("👍 Liked")
            
            if likes_count > 0:
                interaction_parts.append(f"💖 {likes_count} Likes")
            
            if interaction_parts:
                info += f"**Status**: {' | '.join(interaction_parts)}\n"
        
        return info

    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        if not keywords:
            return "None"
        
        display_keywords = keywords[:max_count]
        keyword_text = ", ".join(f"`{kw}`" for kw in display_keywords)
        
        if len(keywords) > max_count:
            keyword_text += f" and {len(keywords)} more"
        
        return keyword_text

    def _truncate_text(self, text: str, max_length: int = 150) -> str:
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rstrip() + "..."

    def _format_date(self, date_str: str) -> str:
        if not date_str:
            return "Unknown"
        
        try:
            from datetime import datetime
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.strftime('%Y-%m-%d')
        except:
            return date_str

    def _safe_get_str(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        value = data.get(key, default)
        return str(value) if value is not None else default

    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        value = data.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def _format_empty_result(self, query: str, entity_type: str) -> str:
        return f"❌ No {entity_type} found related to '{query}'.\n\n💡 Suggestions:\n- Check spelling\n- Try different keywords\n- Use more general search terms"

    def _format_list_header(self, title: str, count: int, query: str) -> str:
        return f"# {title}\n\n**Search Term**: {query}\n**Results Found**: {count}\n\n"

    def _format_error_response(self, error: str, operation: str) -> str:
        return f"❌ {operation} failed\n\n**Error Message**: {error}\n\n💡 Please try again later or contact administrator."
    
    def _format_citations(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        content = f"# 📊 Paper Citation Analysis\n\n"
        
        title = self._safe_get_str(raw_result, 'title')
        doi = self._safe_get_str(raw_result, 'doi')
        url = self._safe_get_str(raw_result, 'url')
        
        content += f"**Paper ID**: `{paper_id}`\n"
        if title:
            content += f"**Paper Title**: {title}\n"
        if doi:
            content += f"**DOI**: {doi}\n"
        if url:
            content += f"**Link**: {url}\n"
        
        content += "\n## 📈 Citation Statistics\n"
        outgoing = self._safe_get_int(raw_result, 'outgoing_citations_count')
        incoming = self._safe_get_int(raw_result, 'incoming_citations_count')
        total = self._safe_get_int(raw_result, 'total_citations_count')
        
        content += f"- **Citations to Other Papers**: {outgoing}\n"
        content += f"- **Citations from Other Papers**: {incoming}\n"
        content += f"- **Total Citation Relations**: {total}\n\n"
        
        citing_papers = raw_result.get('citing_papers', [])
        if citing_papers:
            content += f"## 📄 Papers Citing This Paper ({len(citing_papers)})\n\n"
            for i, paper in enumerate(citing_papers, 1):
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                doi = self._safe_get_str(paper, 'doi')
                url = self._safe_get_str(paper, 'url')
                paper_id = self._safe_get_str(paper, 'id')
                
                content += f"### {i}. {title}\n\n"
                content += f"**Paper ID**: `{paper_id}`\n"
                
                if citations > 0:
                    content += f"**Citations**: {citations}\n"
                
                if cited_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(cited_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d')
                        content += f"**Citation Date**: {formatted_date}\n"
                    except:
                        content += f"**Citation Date**: {cited_at}\n"
                
                if doi:
                    content += f"**DOI**: {doi}\n"
                
                if url:
                    content += f"**Link**: {url}\n"
                
                keywords = paper.get('keywords', [])
                if keywords and keywords != [""]:
                    valid_keywords = [kw for kw in keywords if kw.strip()]
                    if valid_keywords:
                        content += f"**Keywords**: {', '.join(f'`{kw}`' for kw in valid_keywords)}\n"
                
                content += "\n---\n\n"
        else:
            content += "## 📄 Papers Citing This Paper\n\n❌ No other papers have cited this paper yet.\n\n"
        
        cited_papers = raw_result.get('cited_papers', [])
        if cited_papers:
            content += f"## 📚 Papers Cited by This Paper ({len(cited_papers)})\n\n"
            for i, paper in enumerate(cited_papers, 1):
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                doi = self._safe_get_str(paper, 'doi')
                url = self._safe_get_str(paper, 'url')
                paper_id = self._safe_get_str(paper, 'id')
                
                content += f"### {i}. {title}\n\n"
                content += f"**Paper ID**: `{paper_id}`\n"
                
                if citations > 0:
                    content += f"**Citations**: {citations}\n"
                
                if cited_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(cited_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d')
                        content += f"**Citation Date**: {formatted_date}\n"
                    except:
                        content += f"**Citation Date**: {cited_at}\n"
                
                if doi:
                    content += f"**DOI**: {doi}\n"
                
                if url:
                    content += f"**Link**: {url}\n"
                
                keywords = paper.get('keywords', [])
                if keywords and keywords != [""]:
                    valid_keywords = [kw for kw in keywords if kw.strip()]
                    if valid_keywords:
                        content += f"**Keywords**: {', '.join(f'`{kw}`' for kw in valid_keywords)}\n"
                
                content += "\n---\n\n"
        else:
            content += "## 📚 Papers Cited by This Paper\n\n❌ This paper has not cited any other papers.\n\n"
        
        content += "## 🔍 Citation Analysis Summary\n\n"
        
        if incoming > 0:
            content += f"✅ This paper has been cited by **{incoming}** papers, showing academic impact.\n"
        else:
            content += "📝 This paper has not been cited by other papers yet.\n"
        
        if outgoing > 0:
            content += f"📚 This paper cites **{outgoing}** related papers, demonstrating good literature foundation.\n"
        else:
            content += "📝 This paper does not cite any other papers.\n"
        
        return content