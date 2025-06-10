# src/core/tools/trend_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class TrendTools(BaseTools):
    """趋势分析工具 - 支持JSON格式返回"""
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="get_trending_papers",
                description="获取热门论文，分析当前学术热点",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "time_window": {
                            "type": "string",
                            "enum": ["week", "month", "year"],
                            "default": "month",
                            "description": "时间窗口：week(一周), month(一月), year(一年)"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回结果数量"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    }
                }
            ),
            Tool(
                name="get_top_keywords",
                description="获取热门关键词，分析研究热点话题",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回结果数量"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，格式：YYYY-YYYY"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    }
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
                            "description": "研究领域名称"
                        },
                        "time_range": {
                            "type": "string",
                            "default": "2020-2024",
                            "description": "时间范围，格式：YYYY-YYYY"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["publication_count", "citation_count", "author_count"]
                            },
                            "default": ["publication_count"],
                            "description": "分析指标"
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["year", "quarter", "month"],
                            "default": "year",
                            "description": "时间粒度"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["domain"]
                }
            ),
            Tool(
                name="analyze_research_landscape",
                description="分析研究领域全景，包括热点话题、活跃作者、新兴趋势等",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "研究领域名称"
                        },
                        "analysis_dimensions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["topics", "authors", "trends", "institutions"]
                            },
                            "default": ["topics", "authors", "trends"],
                            "description": "分析维度"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["domain"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_trending_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门论文工具 - 支持JSON格式"""
        time_window = arguments.get("time_window", "year")
        limit = arguments.get("limit", 2)
        return_format = arguments.get("format", "json")

        logger.info("Getting trending papers", time_window=time_window, limit=limit, format=return_format)
        
        try:
            raw_result = await self.go_client.get_trending_papers(
                time_window=time_window,
                limit=limit
            )
            
            if return_format == "json":
                # 返回原始 JSON
                # return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
                            # 返回原始 JSON
                json_text = json.dumps(raw_result, ensure_ascii=False, indent=2)
                # 输出到日志
                logger.debug("Returning JSON result", json_content=json_text)
                # 或者使用 info 级别
                logger.info("Trending papers JSON result", 
                        json_length=len(json_text))
                # 如果需要完整内容，可以单独记录
                logger.debug(f"Full JSON response:\n{json_text}")
                return [TextContent(type="text", text=json_text)]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_trending_papers(raw_result, time_window)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Get trending papers failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取热门论文")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_top_keywords(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取热门关键词工具 - 支持JSON格式"""
        limit = arguments.get("limit", 20)
        time_range = arguments.get("time_range")
        return_format = arguments.get("format", "json")
        
        logger.info("Getting top keywords", limit=limit, time_range=time_range, format=return_format)
        
        try:
            raw_result = await self.go_client.get_top_keywords()
            
            # 如果有时间范围限制，可以在这里过滤
            if time_range:
                # 这里可以添加时间范围过滤逻辑
                pass
            
            if return_format == "json":
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_top_keywords(raw_result, limit)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get top keywords failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取热门关键词")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def analyze_domain_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """分析领域趋势工具 - 支持JSON格式"""
        domain = arguments["domain"]
        time_range = arguments.get("time_range", "2020-2024")
        metrics = arguments.get("metrics", ["publication_count"])
        granularity = arguments.get("granularity", "year")
        return_format = arguments.get("format", "json")
        
        logger.info(
            "Analyzing domain trends", 
            domain=domain, 
            time_range=time_range, 
            metrics=metrics,
            granularity=granularity,
            format=return_format
        )
        
        try:
            raw_result = await self.go_client.get_research_trends(
                domain=domain,
                time_range=time_range,
                metrics=metrics,
                granularity=granularity
            )
            
            # if return_format == "json":
                # 返回原始 JSON
            return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            # else:
            #     # 返回格式化的 Markdown（默认）
            #     content = self._format_domain_trends(raw_result, domain)
            #     return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Analyze domain trends failed", error=str(e))
            error_content = self._format_error_response(str(e), "分析领域趋势")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def analyze_research_landscape(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """分析研究全景工具 - 支持JSON格式"""
        domain = arguments["domain"]
        analysis_dimensions = arguments.get("analysis_dimensions", ["topics", "authors", "trends"])
        return_format = arguments.get("format", "json")
        
        logger.info(
            "Analyzing research landscape", 
            domain=domain, 
            analysis_dimensions=analysis_dimensions,
            format=return_format
        )
        
        try:
            raw_result = await self.go_client.analyze_research_landscape(
                domain=domain,
                analysis_dimensions=analysis_dimensions
            )
            
            # if return_format == "json":
            # 返回原始 JSON
            return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            # else:
            #     # 返回格式化的 Markdown（默认）
            #     content = self._format_research_landscape(raw_result, domain)
            #     return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            error_content = self._format_error_response(str(e), "分析研究全景")
            return [TextContent(type="text", text=error_content)]
    
    def _format_trending_papers(self, raw_result: Dict[str, Any], time_window: str) -> str:
        """格式化热门论文结果 - 根据实际API返回数据调整"""
        papers = raw_result.get("trending_papers", [])
        count = raw_result.get("count", len(papers))
        
        time_window_cn = {
            "week": "本周",
            "month": "本月", 
            "year": "本年"
        }.get(time_window, time_window)
        
        content = f"# 📈 {time_window_cn}热门论文\n\n"
        content += f"**时间范围**: {time_window_cn}\n"
        content += f"**论文数量**: {count}\n\n"
        
        if not papers:
            content += f"{time_window_cn}暂无热门论文数据。\n"
            return content
        
        content += f"## 🏆 热门论文排行榜\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            # 基本信息
            content += self._format_paper_basic_info(paper)
            
            # 热度指标 - 使用实际字段名
            popularity_score = paper.get('popularity_score')
            if popularity_score is not None:
                content += f"**🔥 热度评分**: {popularity_score:.3f}\n"
            
            # 引用数
            citations = self._safe_get_int(paper, 'citations')
            if citations > 0:
                content += f"**📊 引用数**: {citations}\n"
            
            # 发表信息
            published_year = self._safe_get_int(paper, 'published_year')
            if published_year > 0:
                content += f"**📅 发表年份**: {published_year}\n"
            
            published_at = self._safe_get_str(paper, 'published_at')
            if published_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y年%m月%d日')
                    content += f"**📅 发表日期**: {formatted_date}\n"
                except:
                    content += f"**📅 发表日期**: {published_at}\n"
            
            # 期刊/会议信息
            venue_name = self._safe_get_str(paper, 'venue_name')
            venue_id = self._safe_get_str(paper, 'venue_id')
            if venue_name:
                content += f"**📖 发表于**: {venue_name}"
                if venue_id and venue_id != venue_name:
                    content += f" ({venue_id})"
                content += "\n"
            
            # DOI 和链接
            doi = self._safe_get_str(paper, 'doi')
            if doi:
                content += f"**🔗 DOI**: {doi}\n"
            
            url = self._safe_get_str(paper, 'url')
            if url:
                content += f"**📄 论文链接**: {url}\n"
            
            # 缩略图
            img_url = self._safe_get_str(paper, 'img_url')
            if img_url:
                content += f"**🖼️ 缩略图**: {img_url}\n"
            
            # 作者信息
            authors = paper.get('authors', [])
            if authors:
                if isinstance(authors[0], str):
                    # 作者是字符串列表
                    content += f"**👥 作者**: {', '.join(authors)}\n"
                else:
                    # 作者是对象列表
                    author_names = []
                    for author in authors:
                        if isinstance(author, dict):
                            name = author.get('name', str(author))
                            author_names.append(name)
                        else:
                            author_names.append(str(author))
                    content += f"**👥 作者**: {', '.join(author_names)}\n"
            
            # 关键词
            keywords = paper.get('keywords', [])
            if keywords and keywords != [""]:
                valid_keywords = [kw for kw in keywords if kw.strip()]
                if valid_keywords:
                    content += f"**🏷️ 关键词**: {self._format_keywords(valid_keywords, max_count=5)}\n"
            
            # 摘要
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"**📝 摘要**: {self._truncate_text(abstract, 200)}\n"
            
            # 论文ID
            paper_id = self._safe_get_str(paper, 'id')
            if paper_id:
                content += f"**🆔 论文ID**: `{paper_id}`\n"
            
            # 添加热度等级指示器
            if popularity_score is not None:
                if popularity_score >= 0.8:
                    content += "**🔥🔥🔥 超高热度**\n"
                elif popularity_score >= 0.6:
                    content += "**🔥🔥 高热度**\n"
                elif popularity_score >= 0.4:
                    content += "**🔥 中等热度**\n"
                else:
                    content += "**📈 新兴热度**\n"
            
            content += "\n---\n\n"
        
        # 添加统计分析
        if len(papers) >= 3:
            content += "## 📊 热门论文分析\n\n"
            
            # 热度分析
            avg_popularity = sum(p.get('popularity_score', 0) for p in papers) / len(papers)
            content += f"- **平均热度评分**: {avg_popularity:.3f}\n"
            
            # 引用分析
            total_citations = sum(self._safe_get_int(p, 'citations') for p in papers)
            avg_citations = total_citations / len(papers)
            content += f"- **总引用数**: {total_citations}\n"
            content += f"- **平均引用数**: {avg_citations:.1f}\n"
            
            # 年份分析
            years = [self._safe_get_int(p, 'published_year') for p in papers if self._safe_get_int(p, 'published_year') > 0]
            if years:
                latest_year = max(years)
                earliest_year = min(years)
                content += f"- **发表年份范围**: {earliest_year} - {latest_year}\n"
            
            # 期刊分析
            venues = [self._safe_get_str(p, 'venue_name') for p in papers if self._safe_get_str(p, 'venue_name')]
            if venues:
                venue_counts = {}
                for venue in venues:
                    venue_counts[venue] = venue_counts.get(venue, 0) + 1
                top_venues = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                content += f"- **主要发表期刊**: {', '.join([f'{v}({c}篇)' for v, c in top_venues])}\n"
            
            # 关键词分析
            all_keywords = []
            for paper in papers:
                keywords = paper.get('keywords', [])
                if keywords and keywords != [""]:
                    all_keywords.extend([kw for kw in keywords if kw.strip()])
            
            if all_keywords:
                keyword_counts = {}
                for kw in all_keywords:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
                top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                content += f"- **热门关键词**: {', '.join([f'{kw}({c})' for kw, c in top_keywords])}\n"
            
            content += "\n"
            # 添加使用提示
            content += "## 💡 使用提示\n\n"
            content += "- 点击论文ID可以获取详细信息\n"
            content += "- 热度评分基于多个因素：引用数、发表时间、关注度等\n"
            content += "- 可以使用关键词进一步搜索相关论文\n\n"
        
        return content

    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        """格式化论文基本信息的辅助方法"""
        info = ""
        
        # 这个方法保持简单，主要信息在主方法中处理
        return info

    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        """格式化关键词列表"""
        if not keywords:
            return "无"
        
        # 限制显示数量
        display_keywords = keywords[:max_count]
        formatted = ', '.join(f'`{kw}`' for kw in display_keywords)
        
        if len(keywords) > max_count:
            formatted += f" 等{len(keywords)}个关键词"
        
        return formatted

    def _truncate_text(self, text: str, max_length: int = 150) -> str:
        """截断文本到指定长度"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        # 在单词边界截断（对于英文）
        truncated = text[:max_length]
        
        # 尝试在句号、感叹号或问号处截断
        for punct in ['. ', '! ', '? ']:
            last_punct = truncated.rfind(punct)
            if last_punct > max_length * 0.7:  # 至少保留70%的长度
                return truncated[:last_punct + 1] + "..."
        
        # 尝试在空格处截断
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # 至少保留80%的长度
            return truncated[:last_space] + "..."
        
        return truncated + "..."

    def _safe_get_str(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        """安全获取字符串值"""
        value = data.get(key, default)
        return str(value) if value is not None else default

    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        """安全获取整数值"""
        value = data.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default


    
    def _format_top_keywords(self, raw_result: Dict[str, Any], limit: int) -> str:
        """格式化热门关键词结果 - 根据实际API返回数据调整"""
        keywords = raw_result.get("keywords", [])
        count = raw_result.get("count", len(keywords))
        
        content = f"# 🏷️ 热门研究关键词\n\n"
        content += f"**关键词总数**: {count}\n"
        content += f"**显示数量**: {min(limit, len(keywords))}\n\n"
        
        if not keywords:
            content += "暂无关键词数据。\n"
            return content
        
        # 限制显示数量
        display_keywords = keywords[:limit]
        
        content += f"## 📊 关键词排行榜 (按论文数量排序)\n\n"
        
        # 计算最大论文数量用于绘制简单的条形图
        max_count = max(kw.get('paper_count', 0) for kw in display_keywords) if display_keywords else 0
        
        for i, keyword_data in enumerate(display_keywords, 1):
            keyword = keyword_data.get('keyword', 'Unknown')
            paper_count = keyword_data.get('paper_count', 0)
            
            # 计算相对热度（用于显示条形图）
            if max_count > 0:
                relative_heat = paper_count / max_count
                bar_length = int(relative_heat * 20)  # 最大20个字符的条形图
                heat_bar = "█" * bar_length + "░" * (20 - bar_length)
            else:
                heat_bar = "░" * 20
            
            # 添加热度等级
            if paper_count >= max_count * 0.8:
                heat_level = "🔥🔥🔥"
            elif paper_count >= max_count * 0.5:
                heat_level = "🔥🔥"
            elif paper_count >= max_count * 0.2:
                heat_level = "🔥"
            else:
                heat_level = "📈"
            
            content += f"### {i}. `{keyword}` {heat_level}\n\n"
            content += f"**📄 论文数量**: {paper_count}\n"
            content += f"**📊 热度条**: {heat_bar} ({relative_heat:.1%})\n"
            
            # 解析关键词类型（如果是学科分类）
            keyword_info = self._parse_keyword_info(keyword)
            if keyword_info:
                content += f"**🏫 领域**: {keyword_info}\n"
            
            content += "\n---\n\n"
        
        # 添加统计分析
        if len(display_keywords) >= 3:
            content += "## 📈 关键词分析\n\n"
            
            # 论文数量统计
            total_papers = sum(kw.get('paper_count', 0) for kw in display_keywords)
            avg_papers = total_papers / len(display_keywords)
            content += f"- **总论文数**: {total_papers}\n"
            content += f"- **平均论文数**: {avg_papers:.1f}\n"
            content += f"- **最热关键词**: `{display_keywords[0].get('keyword', 'N/A')}` ({display_keywords[0].get('paper_count', 0)} 篇论文)\n"
            
            # 学科分布分析
            subject_stats = self._analyze_subject_distribution(display_keywords)
            if subject_stats:
                content += f"- **主要学科领域**: {', '.join([f'{subj}({count}个关键词)' for subj, count in subject_stats[:5]])}\n"
            
            # 热度分布
            high_heat = len([kw for kw in display_keywords if kw.get('paper_count', 0) >= max_count * 0.5])
            medium_heat = len([kw for kw in display_keywords if max_count * 0.2 <= kw.get('paper_count', 0) < max_count * 0.5])
            low_heat = len([kw for kw in display_keywords if kw.get('paper_count', 0) < max_count * 0.2])
            
            content += f"- **热度分布**: 高热度({high_heat}个) | 中等热度({medium_heat}个) | 新兴热度({low_heat}个)\n"
            
            content += "\n"
        
        # 添加使用提示
        content += "## 💡 使用提示\n\n"
        content += "- 可以使用这些关键词搜索相关论文\n"
        content += "- `cs.*` 表示计算机科学相关领域\n"
        content += "- `physics.*` 表示物理学相关领域\n"
        content += "- 数字越大表示该领域的研究越活跃\n\n"
        
        return content

    def _parse_keyword_info(self, keyword: str) -> str:
        """解析关键词信息，特别是学科分类代码"""
        if not keyword:
            return ""
        
        # 常见的学科分类映射
        subject_mapping = {
            # 计算机科学
            "cs.CR": "计算机科学 - 密码学与安全",
            "cs.SE": "计算机科学 - 软件工程", 
            "cs.PL": "计算机科学 - 编程语言",
            "cs.AR": "计算机科学 - 硬件架构",
            "cs.DL": "计算机科学 - 数字图书馆",
            "cs.AI": "计算机科学 - 人工智能",
            "cs.LG": "计算机科学 - 机器学习",
            "cs.CV": "计算机科学 - 计算机视觉",
            "cs.NI": "计算机科学 - 网络与互联网架构",
            "cs.DC": "计算机科学 - 分布式、并行与集群计算",
            "cs.DB": "计算机科学 - 数据库",
            "cs.IR": "计算机科学 - 信息检索",
            "cs.HC": "计算机科学 - 人机交互",
            "cs.CL": "计算机科学 - 计算与语言",
            "cs.GT": "计算机科学 - 计算机科学与博弈论",
            
            # 物理学
            "physics.ed-ph": "物理学 - 物理教育",
            "physics.gen-ph": "物理学 - 普通物理",
            "physics.comp-ph": "物理学 - 计算物理",
            
            # 数学
            "math.CO": "数学 - 组合数学",
            "math.LO": "数学 - 逻辑",
            "math.ST": "数学 - 统计理论",
            
            # 其他常见领域
            "econ.EM": "经济学 - 计量经济学",
            "stat.ML": "统计学 - 机器学习",
            "q-bio.QM": "定量生物学 - 定量方法",
        }
        
        # 直接匹配
        if keyword in subject_mapping:
            return subject_mapping[keyword]
        
        # 模糊匹配主要学科
        if keyword.startswith("cs."):
            return f"计算机科学 - {keyword[3:].upper()}"
        elif keyword.startswith("physics."):
            return f"物理学 - {keyword[8:].replace('-', ' ').title()}"
        elif keyword.startswith("math."):
            return f"数学 - {keyword[5:].upper()}"
        elif keyword.startswith("stat."):
            return f"统计学 - {keyword[5:].upper()}"
        elif keyword.startswith("econ."):
            return f"经济学 - {keyword[5:].upper()}"
        elif keyword.startswith("q-bio."):
            return f"定量生物学 - {keyword[6:].upper()}"
        
        return ""

    def _analyze_subject_distribution(self, keywords: List[Dict[str, Any]]) -> List[tuple]:
        """分析学科分布"""
        subject_counts = {}
        
        for kw_data in keywords:
            keyword = kw_data.get('keyword', '')
            if '.' in keyword:
                subject = keyword.split('.')[0]
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        # 学科名称映射
        subject_names = {
            'cs': '计算机科学',
            'physics': '物理学',
            'math': '数学',
            'stat': '统计学',
            'econ': '经济学',
            'q-bio': '定量生物学'
        }
        
        # 转换为友好名称并排序
        result = []
        for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
            friendly_name = subject_names.get(subject, subject.upper())
            result.append((friendly_name, count))
        
        return result