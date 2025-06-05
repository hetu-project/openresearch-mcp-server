# src/mcp/tools/trend_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent

from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class TrendTools(BaseTools):
    """趋势分析工具 - MVP版本"""
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="get_trending_papers",
                description="获取热门论文趋势",
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
                            "description": "返回结果数量"
                        }
                    }
                }
            ),
            Tool(
                name="get_top_keywords",
                description="获取热门研究话题",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回关键词数量"
                        }
                    }
                }
            )
        ]
    
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
            error_content = self._format_error_response(str(e), "获取热门论文")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_top_keywords(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门关键词工具"""
        limit = arguments.get("limit", 20)
        
        logger.info("Getting top keywords", limit=limit)
        
        try:
            raw_result = await self.go_client.get_top_keywords()
            
            content = self._format_top_keywords(raw_result, limit)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get top keywords failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取热门关键词")
            return [TextContent(type="text", text=error_content)]
    
    def _format_trending_papers(self, raw_result: Dict[str, Any], time_window: str) -> str:
        """格式化热门论文结果"""
        papers = raw_result.get("trending_papers", [])
        count = raw_result.get("count", len(papers))
        
        time_window_cn = {
            "week": "本周",
            "month": "本月", 
            "year": "本年"
        }.get(time_window, time_window)
        
        content = f"# {time_window_cn}热门论文\n\n"
        content += f"**时间范围**: {time_window_cn}\n"
        content += f"**论文数量**: {count}\n\n"
        
        if not papers:
            content += f"{time_window_cn}暂无热门论文数据。\n"
            return content
        
        content += f"## 热门论文排行榜\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            # 基本信息
            content += self._format_paper_basic_info(paper)
            
            # 热度指标
            popularity_score = paper.get('popularity_score')
            if popularity_score is not None:
                content += f"**热度评分**: {popularity_score:.2f}\n"
            
            # 摘要
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"**摘要**: {self._truncate_text(abstract, 150)}\n"
            
            # 关键词
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"**关键词**: {self._format_keywords(keywords, max_count=5)}\n"
            
            # 论文ID
            content += f"**ID**: {self._safe_get_str(paper, 'id', 'N/A')}\n"
            content += "\n---\n\n"
        
        return content
    
    def _format_top_keywords(self, raw_result: Dict[str, Any], limit: int) -> str:
        """格式化热门关键词结果"""
        keywords = raw_result.get("keywords", [])
        count = raw_result.get("count", len(keywords))
        
        content = f"# 热门研究话题\n\n"
        content += f"**关键词总数**: {count}\n"
        content += f"**显示数量**: {min(limit, len(keywords))}\n\n"
        
        if not keywords:
            content += "暂无热门关键词数据。\n"
            return content
        
        content += f"## 热门话题排行榜\n\n"
        
        # 限制显示数量
        display_keywords = keywords[:limit]
        
        for i, keyword_data in enumerate(display_keywords, 1):
            keyword = self._safe_get_str(keyword_data, 'keyword', 'Unknown')
            paper_count = self._safe_get_int(keyword_data, 'paper_count')
            
            content += f"{i}. **{keyword}**"
            if paper_count > 0:
                content += f" ({paper_count} 篇论文)"
            
            # 添加热度指示器
            if i <= 3:
                content += " 🔥"
            elif i <= 10:
                content += " 📈"
            
            content += "\n"
        
        # 添加统计信息
        if len(display_keywords) >= 5:
            total_papers = sum(
                self._safe_get_int(kw, 'paper_count') 
                for kw in display_keywords[:5]
            )
            content += f"\n## 统计信息\n"
            content += f"- 前5个热门话题共涉及 {total_papers} 篇论文\n"
            
            # 计算平均论文数
            if len(display_keywords) > 0:
                avg_papers = sum(
                    self._safe_get_int(kw, 'paper_count') 
                    for kw in display_keywords
                ) / len(display_keywords)
                content += f"- 平均每个话题涉及 {avg_papers:.1f} 篇论文\n"
        
        return content