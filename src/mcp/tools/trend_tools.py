# src/tools/trend_tools.py
from typing import Dict, Any, List
import structlog

from mcp.types import Tool, TextContent
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
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
                            "description": "返回数量"
                        }
                    }
                }
            ),
            Tool(
                name="get_top_keywords",
                description="获取热门研究话题",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="analyze_domain_trends",
                description="分析特定领域的研究趋势",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "研究领域关键词"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，如'2020-2024'"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["publication_trend", "author_activity", "keyword_evolution"],
                            "default": "publication_trend",
                            "description": "分析类型"
                        }
                    },
                    "required": ["domain", "time_range"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_trending_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门论文趋势工具"""
        time_window = arguments.get("time_window", "month")
        limit = arguments.get("limit", 20)
        
        logger.info(
            "Getting trending papers",
            time_window=time_window,
            limit=limit
        )
        
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
    
    @handle_tool_error
    async def get_top_keywords(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门话题工具"""
        logger.info("Getting top keywords")
        
        try:
            raw_result = await self.go_client.get_top_keywords()
            
            content = self._format_top_keywords(raw_result)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get top keywords failed", error=str(e))
            return [TextContent(type="text", text=f"获取热门话题失败: {str(e)}")]
    
    @handle_tool_error
    async def analyze_domain_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """分析领域趋势工具"""
        domain = arguments["domain"]
        time_range = arguments["time_range"]
        analysis_type = arguments.get("analysis_type", "publication_trend")
        
        logger.info(
            "Analyzing domain trends",
            domain=domain,
            time_range=time_range,
            analysis_type=analysis_type
        )
        
        try:
            content = await self._analyze_domain_trends(domain, time_range, analysis_type)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Analyze domain trends failed", error=str(e))
            return [TextContent(type="text", text=f"分析领域趋势失败: {str(e)}")]
    
    def _format_trending_papers(self, raw_result: Dict[str, Any], time_window: str) -> str:
        """格式化热门论文"""
        trending_papers = raw_result.get('trending_papers', [])
        count = raw_result.get('count', len(trending_papers))
        
        content = f"# 热门论文趋势\n\n"
        content += f"**时间窗口**: {time_window}\n"
        content += f"**论文数量**: {count}\n\n"
        
        if not trending_papers:
            content += "暂无热门论文数据。\n"
            return content
        
        content += "## 热门论文排行\n\n"
        
        for i, paper in enumerate(trending_papers, 1):
            content += f"### {i}. {paper.get('title', 'Unknown Title')}\n\n"
            
            # 作者信息
            if paper.get('authors'):
                if isinstance(paper['authors'], list):
                    authors = ", ".join(paper['authors'][:3])
                    if len(paper['authors']) > 3:
                        authors += f" 等 ({len(paper['authors'])}位作者)"
                else:
                    authors = str(paper['authors'])
                content += f"**作者**: {authors}\n"
            
            # 热度指标
            if paper.get('popularity_score'):
                content += f"**热度评分**: {paper['popularity_score']:.2f}\n"
            
            if paper.get('citations') is not None:
                content += f"**引用数**: {paper['citations']}\n"
            
            if paper.get('published_at'):
                content += f"**发表时间**: {paper['published_at'][:10]}\n"
            
            # 关键词
            if paper.get('keywords'):
                keywords = ", ".join(paper['keywords'][:5])
                content += f"**关键词**: {keywords}\n"
            
            # 摘要
            if paper.get('abstract'):
                abstract = paper['abstract'][:150] + "..." if len(paper['abstract']) > 150 else paper['abstract']
                content += f"**摘要**: {abstract}\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _format_top_keywords(self, raw_result: Dict[str, Any]) -> str:
        """格式化热门话题"""
        keywords = raw_result.get('keywords', [])
        count = raw_result.get('count', len(keywords))
        
        content = f"# 热门研究话题\n\n"
        content += f"**话题数量**: {count}\n\n"
        
        if not keywords:
            content += "暂无热门话题数据。\n"
            return content
        
        content += "## 热门话题排行\n\n"
        
        # 按论文数量排序
        sorted_keywords = sorted(keywords, key=lambda x: x.get('paper_count', 0), reverse=True)
        
        for i, keyword in enumerate(sorted_keywords[:20], 1):  # 显示前20个
            content += f"{i}. **{keyword.get('keyword', 'Unknown')}**"
            
            paper_count = keyword.get('paper_count', 0)
            content += f" - {paper_count} 篇论文"
            
            # 计算热度等级
            if paper_count >= 100:
                heat_level = "🔥🔥🔥 超热门"
            elif paper_count >= 50:
                heat_level = "🔥🔥 热门"
            elif paper_count >= 20:
                heat_level = "🔥 活跃"
            else:
                heat_level = "📊 新兴"
            
            content += f" ({heat_level})\n"
        
        # 话题分类统计
        content += "\n## 话题热度分布\n"
        super_hot = len([k for k in keywords if k.get('paper_count', 0) >= 100])
        hot = len([k for k in keywords if 50 <= k.get('paper_count', 0) < 100])
        active = len([k for k in keywords if 20 <= k.get('paper_count', 0) < 50])
        emerging = len([k for k in keywords if k.get('paper_count', 0) < 20])
        
        content += f"- 🔥🔥🔥 超热门话题: {super_hot} 个\n"
        content += f"- 🔥🔥 热门话题: {hot} 个\n"
        content += f"- 🔥 活跃话题: {active} 个\n"
        content += f"- 📊 新兴话题: {emerging} 个\n"
        
        return content
    
    async def _analyze_domain_trends(self, domain: str, time_range: str, analysis_type: str) -> str:
        """分析领域趋势"""
        content = f"# {domain} 领域趋势分析\n\n"
        content += f"**分析时间**: {time_range}\n"
        content += f"**分析类型**: {analysis_type}\n\n"
        
        try:
            # 解析时间范围
            years = time_range.split("-")
            start_year = int(years[0]) if len(years) > 0 else 2020
            end_year = int(years[1]) if len(years) > 1 else 2024
            
            if analysis_type == "publication_trend":
                content += await self._analyze_publication_trend(domain, start_year, end_year)
            elif analysis_type == "author_activity":
                content += await self._analyze_author_activity(domain, start_year, end_year)
            elif analysis_type == "keyword_evolution":
                content += await self._analyze_keyword_evolution(domain, start_year, end_year)
            
        except Exception as e:
            content += f"分析过程中出现错误: {str(e)}\n"
        
        return content
    
    async def _analyze_publication_trend(self, domain: str, start_year: int, end_year: int) -> str:
        """分析发表趋势"""
        content = "## 发表趋势分析\n\n"
        
        yearly_data = []
        total_papers = 0
        total_citations = 0
        
        for year in range(start_year, end_year + 1):
            try:
                # 搜索该年份该领域的论文
                papers_result = await self.go_client.search_papers(
                    query=domain,
                    filters={"year": year},
                    limit=100
                )
                
                papers = papers_result.get("papers", [])
                paper_count = len(papers)
                citation_count = sum(paper.get("citations", 0) for paper in papers)
                
                yearly_data.append({
                    "year": year,
                    "papers": paper_count,
                    "citations": citation_count
                })
                
                total_papers += paper_count
                total_citations += citation_count
                
            except Exception as e:
                logger.warning(f"Failed to get data for year {year}", error=str(e))
                yearly_data.append({"year": year, "papers": 0, "citations": 0})
        
        # 显示年度数据
        content += "### 年度发表统计\n\n"
        content += "```\n"
        content += f"{'年份':<8} {'论文数':<8} {'引用数':<10} {'趋势'}\n"
        content += "-" * 35 + "\n"
        
        prev_papers = None
        for data in yearly_data:
            trend_indicator = ""
            if prev_papers is not None:
                if data["papers"] > prev_papers:
                    trend_indicator = "↗"
                elif data["papers"] < prev_papers:
                    trend_indicator = "↘"
                else:
                    trend_indicator = "→"
            
            content += f"{data['year']:<8} {data['papers']:<8} {data['citations']:<10} {trend_indicator}\n"
            prev_papers = data["papers"]
        
        content += "```\n\n"
        
        # 趋势总结
        if len(yearly_data) >= 2:
            first_year_papers = yearly_data[0]["papers"]
            last_year_papers = yearly_data[-1]["papers"]
            
            if first_year_papers > 0:
                growth_rate = ((last_year_papers - first_year_papers) / first_year_papers) * 100
            else:
                growth_rate = 0
            
            content += "### 趋势总结\n"
            content += f"- 总论文数: {total_papers}\n"
            content += f"- 总引用数: {total_citations}\n"
            content += f"- 年均论文数: {total_papers / len(yearly_data):.1f}\n"
            content += f"- 增长率: {growth_rate:+.1f}%\n"
            
            if growth_rate > 20:
                content += "- 发展态势: 快速增长 📈\n"
            elif growth_rate > 0:
                content += "- 发展态势: 稳定增长 📊\n"
            elif growth_rate > -20:
                content += "- 发展态势: 基本稳定 ➡️\n"
            else:
                content += "- 发展态势: 下降趋势 📉\n"
        
        return content
    
    async def _analyze_author_activity(self, domain: str, start_year: int, end_year: int) -> str:
        """分析作者活跃度"""
        content = "## 作者活跃度分析\n\n"
        
        try:
                    # 获取该领域的论文和作者
            papers_result = await self.go_client.search_papers(
                query=domain,
                filters={"year_from": start_year, "year_to": end_year},
                limit=100
            )
            
            papers = papers_result.get("papers", [])
            
            # 统计作者活跃度
            author_stats = {}
            for paper in papers:
                for author in paper.get("authors", []):
                    author_name = author.get("name", "")
                    if author_name:
                        if author_name not in author_stats:
                            author_stats[author_name] = {
                                "name": author_name,
                                "paper_count": 0,
                                "total_citations": 0,
                                "affiliation": author.get("affiliation", ""),
                                "author_id": author.get("id", "")
                            }
                        author_stats[author_name]["paper_count"] += 1
                        author_stats[author_name]["total_citations"] += paper.get("citations", 0)
            
            # 排序并取前20
            top_authors = sorted(
                author_stats.values(),
                key=lambda x: x["paper_count"],
                reverse=True
            )[:20]
            
            content += f"### 活跃作者排行 (基于{len(papers)}篇论文)\n\n"
            
            for i, author in enumerate(top_authors, 1):
                content += f"{i}. **{author['name']}**\n"
                content += f"   - 论文数: {author['paper_count']}\n"
                content += f"   - 总引用数: {author['total_citations']}\n"
                if author['affiliation']:
                    content += f"   - 机构: {author['affiliation']}\n"
                content += "\n"
            
            # 活跃度统计
            content += "### 作者活跃度分布\n"
            high_activity = len([a for a in author_stats.values() if a["paper_count"] >= 5])
            medium_activity = len([a for a in author_stats.values() if 2 <= a["paper_count"] < 5])
            low_activity = len([a for a in author_stats.values() if a["paper_count"] == 1])
            
            content += f"- 高活跃度作者 (≥5篇): {high_activity} 位\n"
            content += f"- 中等活跃度作者 (2-4篇): {medium_activity} 位\n"
            content += f"- 低活跃度作者 (1篇): {low_activity} 位\n"
            
        except Exception as e:
            content += f"分析作者活跃度时出错: {str(e)}\n"
        
        return content
    
    async def _analyze_keyword_evolution(self, domain: str, start_year: int, end_year: int) -> str:
        """分析关键词演化"""
        content = "## 关键词演化分析\n\n"
        
        try:
            # 获取不同时期的关键词
            mid_year = (start_year + end_year) // 2
            
            # 早期关键词
            early_papers = await self.go_client.search_papers(
                query=domain,
                filters={"year_from": start_year, "year_to": mid_year},
                limit=50
            )
            
            # 近期关键词
            recent_papers = await self.go_client.search_papers(
                query=domain,
                filters={"year_from": mid_year + 1, "year_to": end_year},
                limit=50
            )
            
            # 统计关键词频率
            early_keywords = {}
            recent_keywords = {}
            
            for paper in early_papers.get("papers", []):
                for keyword in paper.get("keywords", []):
                    early_keywords[keyword] = early_keywords.get(keyword, 0) + 1
            
            for paper in recent_papers.get("papers", []):
                for keyword in paper.get("keywords", []):
                    recent_keywords[keyword] = recent_keywords.get(keyword, 0) + 1
            
            # 分析关键词变化
            content += f"### 关键词演化 ({start_year}-{mid_year} vs {mid_year+1}-{end_year})\n\n"
            
            # 新兴关键词
            emerging_keywords = []
            for keyword, count in recent_keywords.items():
                if keyword not in early_keywords and count >= 2:
                    emerging_keywords.append((keyword, count))
            
            emerging_keywords.sort(key=lambda x: x[1], reverse=True)
            
            if emerging_keywords:
                content += "#### 🆕 新兴关键词\n"
                for keyword, count in emerging_keywords[:10]:
                    content += f"- **{keyword}** ({count} 次)\n"
                content += "\n"
            
            # 持续热门关键词
            persistent_keywords = []
            for keyword in early_keywords:
                if keyword in recent_keywords:
                    early_count = early_keywords[keyword]
                    recent_count = recent_keywords[keyword]
                    growth = recent_count - early_count
                    persistent_keywords.append((keyword, early_count, recent_count, growth))
            
            persistent_keywords.sort(key=lambda x: x[2], reverse=True)
            
            if persistent_keywords:
                content += "#### 🔥 持续热门关键词\n"
                for keyword, early, recent, growth in persistent_keywords[:10]:
                    trend = "↗" if growth > 0 else "↘" if growth < 0 else "→"
                    content += f"- **{keyword}**: {early} → {recent} {trend}\n"
                content += "\n"
            
            # 衰退关键词
            declining_keywords = []
            for keyword, count in early_keywords.items():
                if keyword not in recent_keywords and count >= 2:
                    declining_keywords.append((keyword, count))
            
            declining_keywords.sort(key=lambda x: x[1], reverse=True)
            
            if declining_keywords:
                content += "#### 📉 衰退关键词\n"
                for keyword, count in declining_keywords[:5]:
                    content += f"- **{keyword}** (早期: {count} 次)\n"
                content += "\n"
            
            # 关键词多样性分析
            total_early = len(early_keywords)
            total_recent = len(recent_keywords)
            overlap = len(set(early_keywords.keys()) & set(recent_keywords.keys()))
            
            content += "#### 关键词多样性\n"
            content += f"- 早期关键词总数: {total_early}\n"
            content += f"- 近期关键词总数: {total_recent}\n"
            content += f"- 重叠关键词: {overlap}\n"
            if total_early > 0:
                continuity = (overlap / total_early) * 100
                content += f"- 研究连续性: {continuity:.1f}%\n"
            
        except Exception as e:
            content += f"分析关键词演化时出错: {str(e)}\n"
        
        return content

