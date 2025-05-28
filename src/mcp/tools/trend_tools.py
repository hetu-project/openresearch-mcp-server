# src/tools/trend_tools.py
from typing import Dict, Any, List
import structlog

from mcp.types import Tool,TextContent
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
from src.models.data_models import TrendAnalysis, TrendData
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class TrendTools:
    """趋势分析工具 - MVP版本"""
    
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="get_research_trends",
                description="获取研究领域趋势分析",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "研究领域"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，如'2020-2024'"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["publication_count", "citation_count"],
                            "description": "分析指标"
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["month", "quarter", "year"],
                            "default": "year",
                            "description": "时间粒度"
                        }
                    },
                    "required": ["domain", "time_range"]
                }
            ),
            Tool(
                name="analyze_research_landscape",
                description="分析研究领域全景",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "研究领域"
                        },
                        "analysis_dimensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "分析维度"
                        }
                    },
                    "required": ["domain", "analysis_dimensions"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_research_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取研究趋势工具"""
        domain = arguments["domain"]
        time_range = arguments["time_range"]
        metrics = arguments.get("metrics", ["publication_count", "citation_count"])
        granularity = arguments.get("granularity", "year")
        
        logger.info(
            "Getting research trends",
            domain=domain,
            time_range=time_range,
            metrics=metrics
        )
        
        try:
            raw_result = await self.go_client.get_research_trends(
                domain=domain,
                time_range=time_range,
                metrics=metrics,
                granularity=granularity
            )
            
            # 解析趋势数据
            trend_analysis = self._parse_trend_data(raw_result, domain, time_range, metrics)
            
            content = self._format_trend_analysis(trend_analysis)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get research trends failed", error=str(e))
            return [TextContent(type="text", text=f"获取研究趋势失败: {str(e)}")]
    
    @handle_tool_error
    async def analyze_research_landscape(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """分析研究领域全景工具"""
        domain = arguments["domain"]
        analysis_dimensions = arguments["analysis_dimensions"]
        
        logger.info(
            "Analyzing research landscape",
            domain=domain,
            dimensions=analysis_dimensions
        )
        
        try:
            raw_result = await self.go_client.analyze_research_landscape(
                domain=domain,
                analysis_dimensions=analysis_dimensions
            )
            
            content = self._format_landscape_analysis(raw_result, domain)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            return [TextContent(type="text", text=f"分析研究领域全景失败: {str(e)}")]
    
    def _parse_trend_data(
        self, 
        raw_data: Dict[str, Any], 
        domain: str, 
        time_range: str, 
        metrics: List[str]
    ) -> TrendAnalysis:
        """解析趋势数据"""
        data_points = []
        
        for raw_point in raw_data.get("data_points", []):
            point = TrendData(
                time_period=raw_point["time_period"],
                value=raw_point["value"],
                label=raw_point.get("label")
            )
            data_points.append(point)
        
        return TrendAnalysis(
            domain=domain,
            time_range=time_range,
            data_points=data_points,
            metrics=metrics
        )
    
    def _format_trend_analysis(self, trend_analysis: TrendAnalysis) -> str:
        """格式化趋势分析结果"""
        content = f"# 研究趋势分析\n\n"
        content += f"**研究领域**: {trend_analysis.domain}\n"
        content += f"**时间范围**: {trend_analysis.time_range}\n"
        content += f"**分析指标**: {', '.join(trend_analysis.metrics)}\n\n"
        
        if not trend_analysis.data_points:
            content += "暂无趋势数据。\n"
            return content
        
        content += "## 趋势数据\n\n"
        
        # 按时间排序
        sorted_points = sorted(trend_analysis.data_points, key=lambda x: x.time_period)
        
        # 创建简单的文本图表
        content += "```\n"
        content += f"{'时间':<12} {'数值':<10} {'趋势'}\n"
        content += "-" * 30 + "\n"
        
        prev_value = None
        for point in sorted_points:
            trend_indicator = ""
            if prev_value is not None:
                if point.value > prev_value:
                    trend_indicator = "↗"
                elif point.value < prev_value:
                    trend_indicator = "↘"
                else:
                    trend_indicator = "→"
            
            content += f"{point.time_period:<12} {point.value:<10.1f} {trend_indicator}\n"
            prev_value = point.value
        
        content += "```\n\n"
        
        # 趋势总结
        if len(sorted_points) >= 2:
            first_value = sorted_points[0].value
            last_value = sorted_points[-1].value
            change_rate = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
            
            content += "## 趋势总结\n"
            content += f"- 起始值: {first_value:.1f}\n"
            content += f"- 结束值: {last_value:.1f}\n"
            content += f"- 变化率: {change_rate:+.1f}%\n"
            
            if change_rate > 10:
                content += "- 趋势: 显著上升 📈\n"
            elif change_rate > 0:
                content += "- 趋势: 温和上升 📊\n"
            elif change_rate > -10:
                content += "- 趋势: 基本稳定 ➡️\n"
            else:
                content += "- 趋势: 明显下降 📉\n"
        
        return content
    
    def _format_landscape_analysis(self, raw_data: Dict[str, Any], domain: str) -> str:
        """格式化领域全景分析结果"""
        content = f"# 研究领域全景分析\n\n"
        content += f"**研究领域**: {domain}\n\n"
        
        # 热门主题
        if "hot_topics" in raw_data:
            content += "## 热门研究主题\n"
            for i, topic in enumerate(raw_data["hot_topics"][:10], 1):
                content += f"{i}. **{topic['name']}**"
                if "score" in topic:
                    content += f" (热度: {topic['score']:.2f})"
                if "paper_count" in topic:
                    content += f" (论文数: {topic['paper_count']})"
                content += "\n"
            content += "\n"
        
        # 顶级机构
        if "top_institutions" in raw_data:
            content += "## 顶级研究机构\n"
            for i, inst in enumerate(raw_data["top_institutions"][:10], 1):
                content += f"{i}. **{inst['name']}**"
                if "paper_count" in inst:
                    content += f" (论文数: {inst['paper_count']})"
                if "citation_count" in inst:
                    content += f" (引用数: {inst['citation_count']})"
                content += "\n"
            content += "\n"
        
        # 活跃作者
        if "active_authors" in raw_data:
            content += "## 活跃研究者\n"
            for i, author in enumerate(raw_data["active_authors"][:10], 1):
                content += f"{i}. **{author['name']}**"
                if "affiliation" in author:
                    content += f" ({author['affiliation']})"
                if "paper_count" in author:
                    content += f" - {author['paper_count']} 篇论文"
                content += "\n"
            content += "\n"
        
        # 重要会议/期刊
        if "top_venues" in raw_data:
            content += "## 重要发表平台\n"
            for i, venue in enumerate(raw_data["top_venues"][:10], 1):
                content += f"{i}. **{venue['name']}**"
                if "type" in venue:
                    content += f" ({venue['type']})"
                if "paper_count" in venue:
                    content += f" - {venue['paper_count']} 篇论文"
                content += "\n"
            content += "\n"
        
        # 新兴趋势
        if "emerging_trends" in raw_data:
            content += "## 新兴研究趋势\n"
            for i, trend in enumerate(raw_data["emerging_trends"][:5], 1):
                content += f"{i}. **{trend['name']}**"
                if "growth_rate" in trend:
                    content += f" (增长率: {trend['growth_rate']:+.1f}%)"
                if "description" in trend:
                    content += f"\n   {trend['description']}"
                content += "\n"
            content += "\n"
        
        return content

