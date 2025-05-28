# src/tools/paper_tools.py
from typing import Dict, Any, List, Optional
import structlog
from mcp.server.models import Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource
from ..clients.go_client import GoServiceClient
from ..services.data_processor import DataProcessor
from ..models.tool_schemas import (
    SearchPapersInput, SearchPapersOutput,
    GetPaperDetailsInput, GetPaperDetailsOutput
)
from ..utils.error_handler import handle_tool_error

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
                            "description": "搜索查询，支持自然语言和关键词"
                        },
                        "filters": {
                            "type": "object",
                            "description": "过滤条件",
                            "properties": {
                                "year_from": {"type": "integer", "description": "起始年份"},
                                "year_to": {"type": "integer", "description": "结束年份"},
                                "venue": {"type": "string", "description": "会议或期刊名称"},
                                "author": {"type": "string", "description": "作者名称"},
                                "domain": {"type": "string", "description": "研究领域"}
                            }
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["relevance", "date", "citations"],
                            "default": "relevance",
                            "description": "排序方式"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回结果数量"
                        },
                        "offset": {
                            "type": "integer",
                            "minimum": 0,
                            "default": 0,
                            "description": "结果偏移量"
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
                        },
                        "include_citations": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否包含引用信息"
                        }
                    },
                    "required": ["paper_ids"]
                }
            )
        ]
    
    @handle_tool_error
    async def search_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索论文工具"""
        # 验证输入
        input_data = SearchPapersInput(**arguments)
        
        logger.info("Searching papers", query=input_data.query, filters=input_data.filters)
        
        try:
            # 调用Go服务
            raw_result = await self.go_client.search_papers(
                query=input_data.query,
                filters=input_data.filters,
                sort_by=input_data.sort_by,
                limit=input_data.limit,
                offset=input_data.offset
            )
            
            # 处理数据
            processed_result = await self.data_processor.process_search_result(
                raw_result,
                input_data.query,
                input_data.dict()
            )
            
            # 构建输出
            output = SearchPapersOutput(
                success=True,
                data=processed_result,
                execution_time_ms=processed_result.metadata.execution_time_ms
            )
            
            # 格式化返回内容
            content = self._format_search_result(processed_result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            output = SearchPapersOutput(
                success=False,
                error=str(e),
                execution_time_ms=0
            )
            return [TextContent(type="text", text=f"搜索失败: {str(e)}")]
    
    @handle_tool_error
    async def get_paper_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取论文详情工具"""
        # 验证输入
        input_data = GetPaperDetailsInput(**arguments)
        
        logger.info("Getting paper details", paper_ids=input_data.paper_ids)
        
        try:
            # 调用Go服务
            raw_result = await self.go_client.get_paper_details(input_data.paper_ids)
            
            # 简单处理数据
            papers = []
            for raw_paper in raw_result.get("papers", []):
                paper = await self.data_processor._parse_papers([raw_paper])
                papers.extend(paper)
            
            # 构建输出
            output = GetPaperDetailsOutput(
                success=True,
                data=papers,
                execution_time_ms=raw_result.get("execution_time_ms", 0)
            )
            
            # 格式化返回内容
            content = self._format_paper_details(papers)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            output = GetPaperDetailsOutput(
                success=False,
                error=str(e),
                execution_time_ms=0
            )
            return [TextContent(type="text", text=f"获取论文详情失败: {str(e)}")]
    
    def _format_search_result(self, result) -> str:
        """格式化搜索结果"""
        content = f"# 搜索结果\n\n"
        content += f"**查询**: {result.metadata.query}\n"
        content += f"**总数**: {result.metadata.total_count}\n"
        content += f"**执行时间**: {result.metadata.execution_time_ms}ms\n\n"
        
        if not result.papers:
            content += "未找到相关论文。\n"
            return content
        
        content += f"## 论文列表 (显示前{len(result.papers)}篇)\n\n"
        
        for i, paper in enumerate(result.papers, 1):
            content += f"### {i}. {paper.title}\n\n"
            
            # 作者信息
            if paper.authors:
                authors = ", ".join([author.name for author in paper.authors[:3]])
                if len(paper.authors) > 3:
                    authors += f" 等 ({len(paper.authors)}位作者)"
                content += f"**作者**: {authors}\n"
            
            # 发表信息
            if paper.venue:
                content += f"**发表于**: {paper.venue}"
                if paper.publication_date:
                    content += f" ({paper.publication_date.year})"
                content += "\n"
            
            # 引用数
            if paper.citation_count is not None:
                content += f"**引用数**: {paper.citation_count}\n"
            
            # 摘要
            if paper.abstract:
                abstract = paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract
                content += f"**摘要**: {abstract}\n"
            
            # 链接
            if paper.url:
                content += f"**链接**: {paper.url}\n"
            elif paper.doi:
                content += f"**DOI**: {paper.doi}\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_paper_details(self, papers) -> str:
        """格式化论文详情"""
        if not papers:
            return "未找到论文详情。"
        
        content = "# 论文详情\n\n"
        
        for paper in papers:
            content += f"## {paper.title}\n\n"
            
            # 基本信息
            content += "### 基本信息\n"
            content += f"**ID**: {paper.id}\n"
            
            if paper.authors:
                content += "**作者**: \n"
                for author in paper.authors:
                    content += f"- {author.name}"
                    if author.affiliations:
                        content += f" ({', '.join(author.affiliations)})"
                    content += "\n"
            
            if paper.venue:
                content += f"**发表于**: {paper.venue}\n"
            
            if paper.publication_date:
                content += f"**发表时间**: {paper.publication_date.strftime('%Y-%m-%d')}\n"
            
            # 指标
            if paper.citation_count is not None or paper.download_count is not None:
                content += "\n### 影响力指标\n"
                if paper.citation_count is not None:
                    content += f"**引用数**: {paper.citation_count}\n"
                if paper.download_count is not None:
                    content += f"**下载数**: {paper.download_count}\n"
            
            # 关键词
            if paper.keywords:
                content += f"\n**关键词**: {', '.join(paper.keywords)}\n"
            
            # 摘要
            if paper.abstract:
                content += f"\n### 摘要\n{paper.abstract}\n"
            
            # 链接
            content += "\n### 链接\n"
            if paper.url:
                content += f"- [论文链接]({paper.url})\n"
            if paper.doi:
                content += f"- DOI: {paper.doi}\n"
            if paper.arxiv_id:
                content += f"- arXiv: {paper.arxiv_id}\n"
            
            content += "\n---\n\n"
        
        return content