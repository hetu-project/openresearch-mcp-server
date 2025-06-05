# src/mcp/tools/paper_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent

from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class PaperTools(BaseTools):
    """论文相关工具 - MVP版本"""
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="search_papers",
                description="搜索学术论文，支持关键词、作者、时间范围等过滤条件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询，支持论文标题关键词"
                        },
                        "filters": {
                            "type": "object",
                            "description": "过滤条件",
                            "properties": {
                                "keywords": {"type": "string", "description": "关键词"},
                                "author": {"type": "string", "description": "作者名称"},
                                "year": {"type": "integer", "description": "发表年份"},
                                "venue": {"type": "string", "description": "会议或期刊名称"},
                                "doi": {"type": "string", "description": "DOI"}
                            }
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回结果数量"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_paper_details",
                description="获取指定论文的详细信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "论文ID列表"
                        }
                    },
                    "required": ["paper_ids"]
                }
            ),
            Tool(
                name="get_paper_citations",
                description="获取论文的引用关系",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_id": {
                            "type": "string",
                            "description": "论文ID"
                        }
                    },
                    "required": ["paper_id"]
                }
            )
        ]
    
    @handle_tool_error
    async def search_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索论文工具"""
        query = arguments["query"]
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        
        logger.info("Searching papers", query=query, filters=filters)
        
        try:
            raw_result = await self.go_client.search_papers(
                query=query,
                filters=filters,
                limit=limit
            )
            
            content = self._format_search_result(raw_result, query)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            error_content = self._format_error_response(str(e), "论文搜索")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_paper_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取论文详情工具"""
        paper_ids = arguments["paper_ids"]
        
        logger.info("Getting paper details", paper_ids=paper_ids)
        
        try:
            raw_result = await self.go_client.get_paper_details(paper_ids)
            
            content = self._format_paper_details(raw_result)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取论文详情")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_paper_citations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取论文引用工具"""
        paper_id = arguments["paper_id"]
        
        logger.info("Getting paper citations", paper_id=paper_id)
        
        try:
            raw_result = await self.go_client.get_paper_citations(paper_id)
            
            content = self._format_citations(raw_result, paper_id)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper citations failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取论文引用")
            return [TextContent(type="text", text=error_content)]
    
    def _format_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        """格式化搜索结果"""
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        if not papers:
            return self._format_empty_result(query, "论文")
        
        content = self._format_list_header("论文搜索结果", count, query)
        content += f"## 论文列表 (显示前{len(papers)}篇)\n\n"
        
        for i, paper in enumerate(papers, 1):
            content += f"### {i}. {self._safe_get_str(paper, 'title', 'Unknown Title')}\n\n"
            
            # 基本信息
            content += self._format_paper_basic_info(paper)
            
            # 摘要
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"**摘要**: {self._truncate_text(abstract)}\n"
            
            # 关键词
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"**关键词**: {self._format_keywords(keywords)}\n"
            
            # 链接信息
            url = self._safe_get_str(paper, 'url')
            doi = self._safe_get_str(paper, 'doi')
            if url:
                content += f"**链接**: {url}\n"
            elif doi:
                content += f"**DOI**: {doi}\n"
            
            # 论文ID
            content += f"**ID**: {self._safe_get_str(paper, 'id', 'N/A')}\n"
            content += "\n---\n\n"
        
        return content
    
    def _format_paper_details(self, raw_result: Dict[str, Any]) -> str:
        """格式化论文详情"""
        papers = raw_result.get("papers", [])
        
        if not papers:
            return "未找到论文详情。"
        
        content = "# 论文详情\n\n"
        
        for paper in papers:
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"## {title}\n\n"
            
            # 基本信息
            content += "### 基本信息\n"
            content += f"**ID**: {self._safe_get_str(paper, 'id', 'N/A')}\n"
            content += self._format_paper_basic_info(paper)
            
            # 影响力指标
            content += "\n### 影响力指标\n"
            citations = self._safe_get_int(paper, 'citations')
            references_count = self._safe_get_int(paper, 'references_count')
            likes_count = self._safe_get_int(paper, 'likes_count')
            
            if citations > 0:
                content += f"**引用数**: {citations}\n"
            if references_count > 0:
                content += f"**参考文献数**: {references_count}\n"
            if likes_count > 0:
                content += f"**点赞数**: {likes_count}\n"
            
            # 关键词
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"\n**关键词**: {self._format_keywords(keywords, max_count=10)}\n"
            
            # 摘要
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"\n### 摘要\n{abstract}\n"
            
            # 链接
            content += "\n### 链接\n"
            url = self._safe_get_str(paper, 'url')
            doi = self._safe_get_str(paper, 'doi')
            img_url = self._safe_get_str(paper, 'img_url')
            
            if url:
                content += f"- [论文链接]({url})\n"
            if doi:
                content += f"- DOI: {doi}\n"
            if img_url:
                content += f"- [论文预览图]({img_url})\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_citations(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """格式化引用关系"""
        content = f"# 论文引用关系\n\n"
        content += f"**论文ID**: {paper_id}\n"
        
        title = self._safe_get_str(raw_result, 'title')
        if title:
            content += f"**论文标题**: {title}\n"
        
        # 引用统计
        content += "\n## 引用统计\n"
        outgoing = self._safe_get_int(raw_result, 'outgoing_citations_count')
        incoming = self._safe_get_int(raw_result, 'incoming_citations_count')
        total = self._safe_get_int(raw_result, 'total_citations_count')
        
        content += f"- 引用其他论文: {outgoing} 篇\n"
        content += f"- 被其他论文引用: {incoming} 篇\n"
        content += f"- 总引用关系: {total} 条\n\n"
        
        # 被引用论文
        citing_papers = raw_result.get('citing_papers', [])
        if citing_papers:
            content += f"## 引用本文的论文 ({len(citing_papers)}篇)\n\n"
            for i, paper in enumerate(citing_papers[:10], 1):  # 只显示前10篇
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                
                content += f"{i}. **{title}**\n"
                if citations > 0:
                    content += f"   引用数: {citations}\n"
                if cited_at:
                    content += f"   引用时间: {self._format_date(cited_at)}\n"
                content += "\n"
        
        # 引用的论文
        cited_papers = raw_result.get('cited_papers', [])
        if cited_papers:
            content += f"## 本文引用的论文 ({len(cited_papers)}篇)\n\n"
            for i, paper in enumerate(cited_papers[:10], 1):  # 只显示前10篇
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                
                content += f"{i}. **{title}**\n"
                if citations > 0:
                    content += f"   引用数: {citations}\n"
                if cited_at:
                    content += f"   引用时间: {self._format_date(cited_at)}\n"
                content += "\n"
        
        return content