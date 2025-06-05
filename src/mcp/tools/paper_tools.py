# src/tools/paper_tools.py
from typing import Dict, Any, List, Optional
import structlog
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class PaperTools:
    """论文相关工具 - MVP版本"""
    
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
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
            ),
            Tool(
                name="get_trending_papers",
                description="获取热门论文",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "time_window": {
                            "type": "string",
                            "enum": ["week", "month", "year"],
                            "default": "month",
                            "description": "时间窗口"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 20,
                            "description": "返回数量"
                        }
                    }
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
            return [TextContent(type="text", text=f"搜索失败: {str(e)}")]
    
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
            return [TextContent(type="text", text=f"获取论文详情失败: {str(e)}")]
    
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
            return [TextContent(type="text", text=f"获取论文引用失败: {str(e)}")]
    
    @handle_tool_error
    async def get_trending_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门论文工具"""
        time_window = arguments.get("time_window", "month")
        limit = arguments.get("limit", 20)
        
        logger.info("Getting trending papers", time_window=time_window, limit=limit)
        
        try:
            raw_result = await self.go_client.get_trending_papers(
                time_window=time_window,
                limit=limit
            )
            
            content = self._format_trending_papers(raw_result, time_window)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get trending papers failed", error=str(e))
            return [TextContent(type="text", text=f"获取热门论文失败: {str(e)}")]
    
    def _format_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        """格式化搜索结果"""
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        content = f"# 论文搜索结果\n\n"
        content += f"**查询**: {query}\n"
        content += f"**找到**: {count} 篇论文\n\n"
        
        if not papers:
            content += "未找到相关论文。\n"
            return content
        
        content += f"## 论文列表 (显示前{len(papers)}篇)\n\n"
        
        for i, paper in enumerate(papers, 1):
            content += f"### {i}. {paper.get('title', 'Unknown Title')}\n\n"
            
            # 作者信息
            if paper.get('authors'):
                authors = []
                for author in paper['authors'][:3]:  # 只显示前3个作者
                    authors.append(author.get('name', 'Unknown'))
                author_text = ", ".join(authors)
                if len(paper['authors']) > 3:
                    author_text += f" 等 ({len(paper['authors'])}位作者)"
                content += f"**作者**: {author_text}\n"
            
            # 发表信息
            if paper.get('venue_name'):
                content += f"**发表于**: {paper['venue_name']}"
                if paper.get('published_at'):
                    # 提取年份
                    year = paper['published_at'][:4]
                    content += f" ({year})"
                content += "\n"
            
            # 引用数
            if paper.get('citations') is not None:
                content += f"**引用数**: {paper['citations']}\n"
            
            # 摘要
            if paper.get('abstract'):
                abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
                content += f"**摘要**: {abstract}\n"
            
            # 关键词
            if paper.get('keywords'):
                keywords = ", ".join(paper['keywords'][:5])  # 只显示前5个关键词
                content += f"**关键词**: {keywords}\n"
            
            # 链接
            if paper.get('url'):
                content += f"**链接**: {paper['url']}\n"
            elif paper.get('doi'):
                content += f"**DOI**: {paper['doi']}\n"
            
            # 论文ID
            content += f"**ID**: {paper.get('id', 'N/A')}\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_paper_details(self, raw_result: Dict[str, Any]) -> str:
        """格式化论文详情"""
        papers = raw_result.get("papers", [])
        
        if not papers:
            return "未找到论文详情。"
        
        content = "# 论文详情\n\n"
        
        for paper in papers:
            content += f"## {paper.get('title', 'Unknown Title')}\n\n"
            
            # 基本信息
            content += "### 基本信息\n"
            content += f"**ID**: {paper.get('id', 'N/A')}\n"
            
            if paper.get('authors'):
                content += "**作者**: \n"
                for author in paper['authors']:
                    content += f"- {author.get('name', 'Unknown')}"
                    if author.get('id'):
                        content += f" (ID: {author['id']})"
                    content += "\n"
            
            if paper.get('venue_name'):
                content += f"**发表于**: {paper['venue_name']}\n"
            
            if paper.get('published_at'):
                content += f"**发表时间**: {paper['published_at'][:10]}\n"
            
            # 指标
            content += "\n### 影响力指标\n"
            if paper.get('citations') is not None:
                content += f"**引用数**: {paper['citations']}\n"
            if paper.get('references_count') is not None:
                content += f"**参考文献数**: {paper['references_count']}\n"
            if paper.get('likes_count') is not None:
                content += f"**点赞数**: {paper['likes_count']}\n"
            
            # 关键词
            if paper.get('keywords'):
                content += f"\n**关键词**: {', '.join(paper['keywords'])}\n"
            
            # 摘要
            if paper.get('abstract'):
                content += f"\n### 摘要\n{paper['abstract']}\n"
            
            # 链接
            content += "\n### 链接\n"
            if paper.get('url'):
                content += f"- [论文链接]({paper['url']})\n"
            if paper.get('doi'):
                content += f"- DOI: {paper['doi']}\n"
            if paper.get('img_url'):
                content += f"- [论文预览图]({paper['img_url']})\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_citations(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """格式化引用关系"""
        content = f"# 论文引用关系\n\n"
        content += f"**论文ID**: {paper_id}\n"
        
        if raw_result.get('title'):
            content += f"**论文标题**: {raw_result['title']}\n"
        
        # 引用统计
        content += "\n## 引用统计\n"
        content += f"- 引用其他论文: {raw_result.get('outgoing_citations_count', 0)} 篇\n"
        content += f"- 被其他论文引用: {raw_result.get('incoming_citations_count', 0)} 篇\n"
        content += f"- 总引用关系: {raw_result.get('total_citations_count', 0)} 条\n\n"
        
        # 被引用论文
        citing_papers = raw_result.get('citing_papers', [])
        if citing_papers:
            content += f"## 引用本文的论文 ({len(citing_papers)}篇)\n\n"
            for i, paper in enumerate(citing_papers[:10], 1):  # 只显示前10篇
                content += f"{i}. **{paper.get('title', 'Unknown Title')}**\n"
                if paper.get('citations'):
                    content += f"   引用数: {paper['citations']}\n"
                if paper.get('cited_at'):
                    content += f"   引用时间: {paper['cited_at'][:10]}\n"
                content += "\n"
        
        # 引用的论文
        cited_papers = raw_result.get('cited_papers', [])
        if cited_papers:
            content += f"## 本文引用的论文 ({len(cited_papers)}篇)\n\n"
            for i, paper in enumerate(cited_papers[:10], 1):  # 只显示前10篇
                content += f"{i}. **{paper.get('title', 'Unknown Title')}**\n"
                if paper.get('citations'):
                    content += f"   引用数: {paper['citations']}\n"
                if paper.get('cited_at'):
                    content += f"   引用时间: {paper['cited_at'][:10]}\n"
                content += "\n"
        
        return content
    
    def _format_trending_papers(self, raw_result: Dict[str, Any], time_window: str) -> str:
        """格式化热门论文"""
        trending_papers = raw_result.get('trending_papers', [])
        count = raw_result.get('count', len(trending_papers))
        
        content = f"# 热门论文\n\n"
        content += f"**时间窗口**: {time_window}\n"
        content += f"**论文数量**: {count}\n\n"
        
        if not trending_papers:
            content += "暂无热门论文数据。\n"
            return content
        
        for i, paper in enumerate(trending_papers, 1):
            content += f"## {i}. {paper.get('title', 'Unknown Title')}\n\n"
            
            # 作者信息
            if paper.get('authors'):
                if isinstance(paper['authors'], list):
                    authors = ", ".join(paper['authors'][:3])
                    if len(paper['authors']) > 3:
                        authors += f" 等 ({len(paper['authors'])}位作者)"
                else:
                    authors = str(paper['authors'])
                content += f"**作者**: {authors}\n"
            
            # 发表信息
            if paper.get('published_at'):
                content += f"**发表时间**: {paper['published_at'][:10]}\n"
            
            # 热度指标
            if paper.get('popularity_score'):
                content += f"**热度评分**: {paper['popularity_score']:.2f}\n"
            
            if paper.get('citations') is not None:
                content += f"**引用数**: {paper['citations']}\n"
            
            # 摘要
            if paper.get('abstract'):
                abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
                content += f"**摘要**: {abstract}\n"
            
            # 关键词
            if paper.get('keywords'):
                keywords = ", ".join(paper['keywords'][:5])
                content += f"**关键词**: {keywords}\n"
            
            # 链接
            if paper.get('url'):
                content += f"**链接**: {paper['url']}\n"
            elif paper.get('doi'):
                content += f"**DOI**: {paper['doi']}\n"
            
            content += "\n---\n\n"
        
        return content

