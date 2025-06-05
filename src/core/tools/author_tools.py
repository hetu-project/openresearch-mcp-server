# src/mcp/tools/author_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent

from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class AuthorTools(BaseTools):
    """作者相关工具 - MVP版本"""
    
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
            error_content = self._format_error_response(str(e), "作者搜索")
            return [TextContent(type="text", text=error_content)]
    
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
            error_content = self._format_error_response(str(e), "获取作者详情")
            return [TextContent(type="text", text=error_content)]
    
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
            error_content = self._format_error_response(str(e), "获取作者论文")
            return [TextContent(type="text", text=error_content)]
    
    def _format_author_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        """格式化作者搜索结果"""
        authors = raw_result.get("authors", [])
        count = raw_result.get("count", len(authors))
        
        if not authors:
            return self._format_empty_result(query, "作者")
        
        content = self._format_list_header("作者搜索结果", count, query)
        
        for i, author in enumerate(authors, 1):
            name = self._safe_get_str(author, 'name', 'Unknown Author')
            content += f"## {i}. {name}\n\n"
            
            # 基本信息
            content += self._format_author_basic_info(author)
            
            # 研究兴趣
            interests = author.get('research_interests')
            if interests:
                content += f"**研究兴趣**: {', '.join(interests)}\n"
            
            # 邮箱
            email = self._safe_get_str(author, 'email')
            if email:
                content += f"**邮箱**: {email}\n"
            
            # 合作者信息
            coauthors = author.get('coauthors', [])
            if coauthors:
                content += f"**主要合作者**: {len(coauthors)} 位\n"
                # 显示前3位合作者
                for j, coauthor in enumerate(coauthors[:3], 1):
                    coauthor_name = self._safe_get_str(coauthor, 'name')
                    collaboration_count = self._safe_get_int(coauthor, 'collaboration_count')
                    if coauthor_name:
                        content += f"  {j}. {coauthor_name}"
                        if collaboration_count > 0:
                            content += f" (合作{collaboration_count}次)"
                        content += "\n"
            
            # 作者ID
            content += f"**ID**: {self._safe_get_str(author, 'id', 'N/A')}\n"
            content += "\n---\n\n"
        
        return content
    
    def _format_author_details(self, raw_result: Dict[str, Any]) -> str:
        """格式化作者详情"""
        authors = raw_result.get("authors", [])
        
        if not authors:
            return "未找到作者详情。"
        
        content = "# 作者详情\n\n"
        
        for author in authors:
            name = self._safe_get_str(author, 'name', 'Unknown Author')
            content += f"## {name}\n\n"
            
            # 基本信息
            content += "### 基本信息\n"
            content += f"**ID**: {self._safe_get_str(author, 'id', 'N/A')}\n"
            content += self._format_author_basic_info(author)
            
            # 联系信息
            email = self._safe_get_str(author, 'email')
            if email:
                content += f"**邮箱**: {email}\n"
            
            # 研究兴趣
            interests = author.get('research_interests')
            if interests:
                content += f"**研究兴趣**: {', '.join(interests)}\n"
            
            # 学术指标
            content += "\n### 学术指标\n"
            h_index = self._safe_get_int(author, 'h_index')
            citation_count = self._safe_get_int(author, 'citation_count')
            paper_count = self._safe_get_int(author, 'paper_count')
            
            if h_index > 0:
                content += f"**H指数**: {h_index}\n"
            if citation_count > 0:
                content += f"**总引用数**: {citation_count}\n"
            if paper_count > 0:
                content += f"**论文数量**: {paper_count}\n"
            
            # 合作网络
            coauthors = author.get('coauthors', [])
            if coauthors:
                content += f"\n### 合作网络 ({len(coauthors)} 位合作者)\n"
                for i, coauthor in enumerate(coauthors[:10], 1):  # 显示前10位
                    coauthor_name = self._safe_get_str(coauthor, 'name')
                    collaboration_count = self._safe_get_int(coauthor, 'collaboration_count')
                    affiliation = self._safe_get_str(coauthor, 'affiliation')
                    
                    content += f"{i}. **{coauthor_name}**"
                    if collaboration_count > 0:
                        content += f" (合作{collaboration_count}次)"
                    if affiliation:
                        content += f" - {affiliation}"
                    content += "\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_author_papers(self, raw_result: Dict[str, Any], author_id: str) -> str:
        """格式化作者论文"""
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        content = f"# 作者发表论文\n\n"
        content += f"**作者ID**: {author_id}\n"
        content += f"**论文总数**: {count}\n\n"
        
        if not papers:
            content += "该作者暂无论文记录。\n"
            return content
        
        content += f"## 论文列表 (显示前{len(papers)}篇)\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            # 发表信息
            published_at = self._safe_get_str(paper, 'published_at')
            if published_at:
                content += f"**发表时间**: {self._format_date(published_at)}\n"
            
            # 作者顺序
            author_order = self._safe_get_int(paper, 'author_order')
            if author_order > 0:
                content += f"**作者顺序**: 第{author_order}作者\n"
            
            # 是否通讯作者
            is_corresponding = paper.get('is_corresponding')
            if is_corresponding:
                content += f"**通讯作者**: 是\n"
            
            # 论文ID
            paper_id = self._safe_get_str(paper, 'id')
            if paper_id:
                content += f"**论文ID**: {paper_id}\n"
            
            content += "\n"
        
        return content

