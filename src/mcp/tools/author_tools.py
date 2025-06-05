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
                            "description": "作者姓名查询"
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
            ),
            Tool(
                name="get_author_papers",
                description="获取作者发表的论文",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "作者ID"
                        }
                    },
                    "required": ["author_id"]
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
            
            content = self._format_author_search_result(raw_result, query)
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
            
            content = self._format_author_details(raw_result)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get author details failed", error=str(e))
            return [TextContent(type="text", text=f"获取作者详情失败: {str(e)}")]
    
    @handle_tool_error
    async def get_author_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取作者论文工具"""
        author_id = arguments["author_id"]
        
        logger.info("Getting author papers", author_id=author_id)
        
        try:
            raw_result = await self.go_client.get_author_papers(author_id)
            
            content = self._format_author_papers(raw_result, author_id)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get author papers failed", error=str(e))
            return [TextContent(type="text", text=f"获取作者论文失败: {str(e)}")]
    
    def _format_author_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        """格式化作者搜索结果"""
        authors = raw_result.get("authors", [])
        
        content = f"# 作者搜索结果\n\n"
        content += f"**查询**: {query}\n"
        content += f"**找到**: {len(authors)} 位作者\n\n"
        
        if not authors:
            content += "未找到相关作者。\n"
            return content
        
        for i, author in enumerate(authors, 1):
            content += f"## {i}. {author.get('name', 'Unknown')}\n\n"
            
            # 基本信息
            content += f"**ID**: {author.get('id', 'N/A')}\n"
            
            if author.get('affiliation'):
                content += f"**机构**: {author['affiliation']}\n"
            
            if author.get('email'):
                content += f"**邮箱**: {author['email']}\n"
            
            # 学术指标
            if author.get('h_index') is not None:
                content += f"**H指数**: {author['h_index']}\n"
            
            if author.get('citation_count') is not None:
                content += f"**引用数**: {author['citation_count']}\n"
            
            if author.get('paper_count') is not None:
                content += f"**论文数**: {author['paper_count']}\n"
            
            # 研究兴趣
            if author.get('research_interests'):
                interests = author['research_interests']
                if isinstance(interests, list):
                    content += f"**研究兴趣**: {', '.join(interests)}\n"
                else:
                    content += f"**研究兴趣**: {interests}\n"
            
            # 合作者信息
            if author.get('coauthors'):
                coauthor_count = len(author['coauthors'])
                content += f"**合作者数量**: {coauthor_count}\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_author_details(self, raw_result: Dict[str, Any]) -> str:
        """格式化作者详情"""
        authors = raw_result.get("authors", [])
        
        if not authors:
            return "未找到作者详情。"
        
        content = "# 作者详情\n\n"
        
        for author in authors:
            content += f"## {author.get('name', 'Unknown')}\n\n"
            
            # 基本信息
            content += "### 基本信息\n"
            content += f"**ID**: {author.get('id', 'N/A')}\n"
            
            if author.get('email'):
                content += f"**邮箱**: {author['email']}\n"
            
            if author.get('affiliation'):
                content += f"**机构**: {author['affiliation']}\n"
            
            if author.get('research_interests'):
                interests = author['research_interests']
                if isinstance(interests, list):
                    content += f"**研究兴趣**: {', '.join(interests)}\n"
                else:
                    content += f"**研究兴趣**: {interests}\n"
            
            # 学术指标
            content += "\n### 学术指标\n"
            if author.get('h_index') is not None:
                content += f"**H指数**: {author['h_index']}\n"
            if author.get('citation_count') is not None:
                content += f"**总引用数**: {author['citation_count']}\n"
            if author.get('paper_count') is not None:
                content += f"**论文数量**: {author['paper_count']}\n"
            
            # 合作者信息
            if author.get('coauthors'):
                content += "\n### 主要合作者\n"
                coauthors = author['coauthors'][:5]  # 只显示前5个
                for coauthor in coauthors:
                    content += f"- **{coauthor.get('name', 'Unknown')}**"
                    if coauthor.get('collaboration_count'):
                        content += f" (合作 {coauthor['collaboration_count']} 次)"
                    if coauthor.get('affiliation'):
                        content += f" - {coauthor['affiliation']}"
                    content += "\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_author_papers(self, raw_result: Dict[str, Any], author_id: str) -> str:
        """格式化作者论文"""
        papers = raw_result.get("papers", [])
        
        content = f"# 作者论文列表\n\n"
        content += f"**作者ID**: {author_id}\n"
        content += f"**论文数量**: {len(papers)}\n\n"
        
        if not papers:
            content += "该作者暂无论文记录。\n"
            return content
        
        for i, paper in enumerate(papers, 1):
            content += f"## {i}. {paper.get('title', 'Unknown Title')}\n\n"
            
            # 发表信息
            if paper.get('published_at'):
                content += f"**发表时间**: {paper['published_at'][:10]}\n"
            
            # 作者顺序
            if paper.get('author_order'):
                content += f"**作者顺序**: 第 {paper['author_order']} 作者"
                if paper.get('is_corresponding'):
                    content += " (通讯作者)"
                content += "\n"
            
            # 论文ID
            if paper.get('id'):
                content += f"**论文ID**: {paper['id']}\n"
            
            content += "\n---\n\n"
        
        return content
