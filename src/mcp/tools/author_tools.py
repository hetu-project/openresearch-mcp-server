# src/tools/author_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent

from src.clients.go_client import GoServiceClient 
from src.services.data_processor import DataProcessor
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class AuthorTools:
    """作者相关工具 - MVP版本"""
    
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="search_authors",
                description="搜索学术作者",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "作者查询"
                        },
                        "filters": {
                            "type": "object",
                            "description": "过滤条件",
                            "properties": {
                                "affiliation": {"type": "string", "description": "机构名称"},
                                "research_area": {"type": "string", "description": "研究领域"}
                            }
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_author_details",
                description="获取作者详细信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "作者ID列表"
                        }
                    },
                    "required": ["author_ids"]
                }
            )
        ]
    
    @handle_tool_error
    async def search_authors(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索作者工具"""
        query = arguments["query"]
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        
        logger.info("Searching authors", query=query, filters=filters)
        
        try:
            raw_result = await self.go_client.search_authors(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # 简单处理数据
            authors = []
            for raw_author in raw_result.get("authors", []):
                author = self.data_processor._parse_author(raw_author)
                authors.append(author)
            
            content = self._format_author_search_result(authors, query)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            return [TextContent(type="text", text=f"搜索作者失败: {str(e)}")]
    
    @handle_tool_error
    async def get_author_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取作者详情工具"""
        author_ids = arguments["author_ids"]
        
        logger.info("Getting author details", author_ids=author_ids)
        
        try:
            raw_result = await self.go_client.get_author_details(author_ids)
            
            authors = []
            for raw_author in raw_result.get("authors", []):
                author = self.data_processor._parse_author(raw_author)
                authors.append(author)
            
            content = self._format_author_details(authors)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get author details failed", error=str(e))
            return [TextContent(type="text", text=f"获取作者详情失败: {str(e)}")]
    
    def _format_author_search_result(self, authors, query: str) -> str:
        """格式化作者搜索结果"""
        content = f"# 作者搜索结果\n\n"
        content += f"**查询**: {query}\n"
        content += f"**找到**: {len(authors)} 位作者\n\n"
        
        if not authors:
            content += "未找到相关作者。\n"
            return content
        
        for i, author in enumerate(authors, 1):
            content += f"## {i}. {author.name}\n\n"
            
            if author.affiliations:
                content += f"**机构**: {', '.join(author.affiliations)}\n"
            
            if author.research_interests:
                content += f"**研究兴趣**: {', '.join(author.research_interests)}\n"
            
            if author.h_index is not None:
                content += f"**H指数**: {author.h_index}\n"
            
            if author.citation_count is not None:
                content += f"**引用数**: {author.citation_count}\n"
            
            if author.paper_count is not None:
                content += f"**论文数**: {author.paper_count}\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_author_details(self, authors) -> str:
        """格式化作者详情"""
        if not authors:
            return "未找到作者详情。"
        
        content = "# 作者详情\n\n"
        
        for author in authors:
            content += f"## {author.name}\n\n"
            
            content += "### 基本信息\n"
            content += f"**ID**: {author.id}\n"
            
            if author.email:
                content += f"**邮箱**: {author.email}\n"
            
            if author.orcid:
                content += f"**ORCID**: {author.orcid}\n"
            
            if author.affiliations:
                content += f"**机构**: {', '.join(author.affiliations)}\n"
            
            if author.research_interests:
                content += f"**研究兴趣**: {', '.join(author.research_interests)}\n"
            
            content += "\n### 学术指标\n"
            if author.h_index is not None:
                content += f"**H指数**: {author.h_index}\n"
            if author.citation_count is not None:
                content += f"**总引用数**: {author.citation_count}\n"
            if author.paper_count is not None:
                content += f"**论文数量**: {author.paper_count}\n"
            
            content += "\n---\n\n"
        
        return content