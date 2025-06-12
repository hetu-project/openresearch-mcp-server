from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class TrendTools(BaseTools):
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_trending_papers",
                description="Get trending papers and analyze current academic hotspots",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "time_window": {
                            "type": "string",
                            "enum": ["week", "month", "year"],
                            "default": "month",
                            "description": "Time window: week, month, year"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "Number of results to return"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown (formatted display) or json (raw data)"
                        }
                    }
                }
            ),
            Tool(
                name="get_top_keywords",
                description="Get trending keywords and analyze hot research topics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "Number of results to return"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range, format: YYYY-YYYY"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown (formatted display) or json (raw data)"
                        }
                    }
                }
            ),
            Tool(
                name="analyze_domain_trends",
                description="Analyze research trends in specific domains",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Research domain name"
                        },
                        "time_range": {
                            "type": "string",
                            "default": "2020-2024",
                            "description": "Time range, format: YYYY-YYYY"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["publication_count", "citation_count", "author_count"]
                            },
                            "default": ["publication_count"],
                            "description": "Analysis metrics"
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["year", "quarter", "month"],
                            "default": "year",
                            "description": "Time granularity"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown (formatted display) or json (raw data)"
                        }
                    },
                    "required": ["domain"]
                }
            ),
            Tool(
                name="analyze_research_landscape",
                description="Analyze research landscape including hot topics, active authors, emerging trends, etc.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Research domain name"
                        },
                        "analysis_dimensions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["topics", "authors", "trends", "institutions"]
                            },
                            "default": ["topics", "authors", "trends"],
                            "description": "Analysis dimensions"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown (formatted display) or json (raw data)"
                        }
                    },
                    "required": ["domain"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_trending_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
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
                json_text = json.dumps(raw_result, ensure_ascii=False, indent=2)
                logger.debug("Returning JSON result", json_content=json_text)
                logger.info("Trending papers JSON result", 
                        json_length=len(json_text))
                logger.debug(f"Full JSON response:\n{json_text}")
                return [TextContent(type="text", text=json_text)]
            else:
                content = self._format_trending_papers(raw_result, time_window)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Get trending papers failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get trending papers")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_top_keywords(self, arguments: Dict[str, Any]) -> List[TextContent]:
        limit = arguments.get("limit", 20)
        time_range = arguments.get("time_range")
        return_format = arguments.get("format", "json")
        
        logger.info("Getting top keywords", limit=limit, time_range=time_range, format=return_format)
        
        try:
            raw_result = await self.go_client.get_top_keywords()
            
            if time_range:
                pass
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_top_keywords(raw_result, limit)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get top keywords failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get top keywords")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def analyze_domain_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
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
            
            return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            
        except Exception as e:
            logger.error("Analyze domain trends failed", error=str(e))
            error_content = self._format_error_response(str(e), "Analyze domain trends")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def analyze_research_landscape(self, arguments: Dict[str, Any]) -> List[TextContent]:
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
            
            return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            error_content = self._format_error_response(str(e), "Analyze research landscape")
            return [TextContent(type="text", text=error_content)]
    
    def _format_trending_papers(self, raw_result: Dict[str, Any], time_window: str) -> str:
        papers = raw_result.get("trending_papers", [])
        count = raw_result.get("count", len(papers))
        
        time_window_en = {
            "week": "This Week",
            "month": "This Month", 
            "year": "This Year"
        }.get(time_window, time_window)
        
        content = f"# 📈 {time_window_en} Trending Papers\n\n"
        content += f"**Time Range**: {time_window_en}\n"
        content += f"**Paper Count**: {count}\n\n"
        
        if not papers:
            content += f"No trending papers data for {time_window_en}.\n"
            return content
        
        content += f"## 🏆 Trending Papers Ranking\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            popularity_score = paper.get('popularity_score')
            if popularity_score is not None:
                content += f"**🔥 Popularity Score**: {popularity_score:.3f}\n"
            
            citations = self._safe_get_int(paper, 'citations')
            if citations > 0:
                content += f"**📊 Citations**: {citations}\n"
            
            published_year = self._safe_get_int(paper, 'published_year')
            if published_year > 0:
                content += f"**📅 Published Year**: {published_year}\n"
            
            published_at = self._safe_get_str(paper, 'published_at')
            if published_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                    content += f"**📅 Published Date**: {formatted_date}\n"
                except:
                    content += f"**📅 Published Date**: {published_at}\n"
            
            venue_name = self._safe_get_str(paper, 'venue_name')
            venue_id = self._safe_get_str(paper, 'venue_id')
            if venue_name:
                content += f"**📖 Published In**: {venue_name}"
                if venue_id and venue_id != venue_name:
                    content += f" ({venue_id})"
                content += "\n"
            
            doi = self._safe_get_str(paper, 'doi')
            if doi:
                content += f"**🔗 DOI**: {doi}\n"
            
            url = self._safe_get_str(paper, 'url')
            if url:
                content += f"**📄 Paper Link**: {url}\n"
            
            img_url = self._safe_get_str(paper, 'img_url')
            if img_url:
                content += f"**🖼️ Thumbnail**: {img_url}\n"
            
            authors = paper.get('authors', [])
            if authors:
                if isinstance(authors[0], str):
                    content += f"**👥 Authors**: {', '.join(authors)}\n"
                else:
                    author_names = []
                    for author in authors:
                        if isinstance(author, dict):
                            name = author.get('name', str(author))
                            author_names.append(name)
                        else:
                            author_names.append(str(author))
                    content += f"**👥 Authors**: {', '.join(author_names)}\n"
            
            keywords = paper.get('keywords', [])
            if keywords and keywords != [""]:
                valid_keywords = [kw for kw in keywords if kw.strip()]
                if valid_keywords:
                    content += f"**🏷️ Keywords**: {self._format_keywords(valid_keywords, max_count=5)}\n"
            
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"**📝 Abstract**: {self._truncate_text(abstract, 200)}\n"
            
            paper_id = self._safe_get_str(paper, 'id')
            if paper_id:
                content += f"**🆔 Paper ID**: `{paper_id}`\n"
            
            if popularity_score is not None:
                if popularity_score >= 0.8:
                    content += "**🔥🔥🔥 Very High Popularity**\n"
                elif popularity_score >= 0.6:
                    content += "**🔥🔥 High Popularity**\n"
                elif popularity_score >= 0.4:
                    content += "**🔥 Medium Popularity**\n"
                else:
                    content += "**📈 Emerging Popularity**\n"
            
            content += "\n---\n\n"
        
        if len(papers) >= 3:
            content += "## 📊 Trending Papers Analysis\n\n"
            
            avg_popularity = sum(p.get('popularity_score', 0) for p in papers) / len(papers)
            content += f"- **Average Popularity Score**: {avg_popularity:.3f}\n"
            
            total_citations = sum(self._safe_get_int(p, 'citations') for p in papers)
            avg_citations = total_citations / len(papers)
            content += f"- **Total Citations**: {total_citations}\n"
            content += f"- **Average Citations**: {avg_citations:.1f}\n"
            
            years = [self._safe_get_int(p, 'published_year') for p in papers if self._safe_get_int(p, 'published_year') > 0]
            if years:
                latest_year = max(years)
                earliest_year = min(years)
                content += f"- **Publication Year Range**: {earliest_year} - {latest_year}\n"
            
            venues = [self._safe_get_str(p, 'venue_name') for p in papers if self._safe_get_str(p, 'venue_name')]
            if venues:
                venue_counts = {}
                for venue in venues:
                    venue_counts[venue] = venue_counts.get(venue, 0) + 1
                top_venues = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                content += f"- **Main Publication Venues**: {', '.join([f'{v}({c} papers)' for v, c in top_venues])}\n"
            
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
                content += f"- **Popular Keywords**: {', '.join([f'{kw}({c})' for kw, c in top_keywords])}\n"
            
            content += "\n"
            content += "## 💡 Usage Tips\n\n"
            content += "- Click on Paper ID for detailed information\n"
            content += "- Popularity score is based on multiple factors: citations, publication date, attention, etc.\n"
            content += "- Use keywords to search for related papers\n\n"
        
        return content

    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        info = ""
        
        return info

    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        if not keywords:
            return "None"
        
        display_keywords = keywords[:max_count]
        formatted = ', '.join(f'`{kw}`' for kw in display_keywords)
        
        if len(keywords) > max_count:
            formatted += f" and {len(keywords)} more keywords"
        
        return formatted

    def _truncate_text(self, text: str, max_length: int = 150) -> str:
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        
        for punct in ['. ', '! ', '? ']:
            last_punct = truncated.rfind(punct)
            if last_punct > max_length * 0.7:
                return truncated[:last_punct + 1] + "..."
        
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            return truncated[:last_space] + "..."
        
        return truncated + "..."

    def _safe_get_str(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        value = data.get(key, default)
        return str(value) if value is not None else default

    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        value = data.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default


    
    def _format_top_keywords(self, raw_result: Dict[str, Any], limit: int) -> str:
        keywords = raw_result.get("keywords", [])
        count = raw_result.get("count", len(keywords))
        
        content = f"# 🏷️ Popular Research Keywords\n\n"
        content += f"**Total Keywords**: {count}\n"
        content += f"**Display Count**: {min(limit, len(keywords))}\n\n"
        
        if not keywords:
            content += "No keyword data available.\n"
            return content
        
        display_keywords = keywords[:limit]
        
        content += f"## 📊 Keyword Rankings (Sorted by Paper Count)\n\n"
        
        max_count = max(kw.get('paper_count', 0) for kw in display_keywords) if display_keywords else 0
        
        for i, keyword_data in enumerate(display_keywords, 1):
            keyword = keyword_data.get('keyword', 'Unknown')
            paper_count = keyword_data.get('paper_count', 0)
            
            if max_count > 0:
                relative_heat = paper_count / max_count
                bar_length = int(relative_heat * 20)
                heat_bar = "█" * bar_length + "░" * (20 - bar_length)
            else:
                heat_bar = "░" * 20
            
            if paper_count >= max_count * 0.8:
                heat_level = "🔥🔥🔥"
            elif paper_count >= max_count * 0.5:
                heat_level = "🔥🔥"
            elif paper_count >= max_count * 0.2:
                heat_level = "🔥"
            else:
                heat_level = "📈"
            
            content += f"### {i}. `{keyword}` {heat_level}\n\n"
            content += f"**📄 Paper Count**: {paper_count}\n"
            content += f"**📊 Heat Bar**: {heat_bar} ({relative_heat:.1%})\n"
            
            keyword_info = self._parse_keyword_info(keyword)
            if keyword_info:
                content += f"**🏫 Field**: {keyword_info}\n"
            
            content += "\n---\n\n"
        
        if len(display_keywords) >= 3:
            content += "## 📈 Keyword Analysis\n\n"
            
            total_papers = sum(kw.get('paper_count', 0) for kw in display_keywords)
            avg_papers = total_papers / len(display_keywords)
            content += f"- **Total Papers**: {total_papers}\n"
            content += f"- **Average Papers**: {avg_papers:.1f}\n"
            content += f"- **Hottest Keyword**: `{display_keywords[0].get('keyword', 'N/A')}` ({display_keywords[0].get('paper_count', 0)} papers)\n"
            
            subject_stats = self._analyze_subject_distribution(display_keywords)
            if subject_stats:
                content += f"- **Main Subject Areas**: {', '.join([f'{subj}({count} keywords)' for subj, count in subject_stats[:5]])}\n"
            
            high_heat = len([kw for kw in display_keywords if kw.get('paper_count', 0) >= max_count * 0.5])
            medium_heat = len([kw for kw in display_keywords if max_count * 0.2 <= kw.get('paper_count', 0) < max_count * 0.5])
            low_heat = len([kw for kw in display_keywords if kw.get('paper_count', 0) < max_count * 0.2])
            
            content += f"- **Heat Distribution**: High Heat({high_heat}) | Medium Heat({medium_heat}) | Emerging Heat({low_heat})\n"
            
            content += "\n"
        
        content += "## 💡 Usage Tips\n\n"
        content += "- Use these keywords to search for related papers\n"
        content += "- `cs.*` represents Computer Science related fields\n"
        content += "- `physics.*` represents Physics related fields\n"
        content += "- Higher numbers indicate more active research in the field\n\n"
        
        return content

    def _parse_keyword_info(self, keyword: str) -> str:
        if not keyword:
            return ""
        
        subject_mapping = {
            "cs.CR": "Computer Science - Cryptography and Security",
            "cs.SE": "Computer Science - Software Engineering", 
            "cs.PL": "Computer Science - Programming Languages",
            "cs.AR": "Computer Science - Hardware Architecture",
            "cs.DL": "Computer Science - Digital Libraries",
            "cs.AI": "Computer Science - Artificial Intelligence",
            "cs.LG": "Computer Science - Machine Learning",
            "cs.CV": "Computer Science - Computer Vision",
            "cs.NI": "Computer Science - Networking and Internet Architecture",
            "cs.DC": "Computer Science - Distributed, Parallel, and Cluster Computing",
            "cs.DB": "Computer Science - Databases",
            "cs.IR": "Computer Science - Information Retrieval",
            "cs.HC": "Computer Science - Human-Computer Interaction",
            "cs.CL": "Computer Science - Computation and Language",
            "cs.GT": "Computer Science - Computer Science and Game Theory",
            
            "physics.ed-ph": "Physics - Physics Education",
            "physics.gen-ph": "Physics - General Physics",
            "physics.comp-ph": "Physics - Computational Physics",
            
            "math.CO": "Mathematics - Combinatorics",
            "math.LO": "Mathematics - Logic",
            "math.ST": "Mathematics - Statistics Theory",
            
            "econ.EM": "Economics - Econometrics",
            "stat.ML": "Statistics - Machine Learning",
            "q-bio.QM": "Quantitative Biology - Quantitative Methods",
        }
        
        if keyword in subject_mapping:
            return subject_mapping[keyword]
        
        if keyword.startswith("cs."):
            return f"Computer Science - {keyword[3:].upper()}"
        elif keyword.startswith("physics."):
            return f"Physics - {keyword[8:].replace('-', ' ').title()}"
        elif keyword.startswith("math."):
            return f"Mathematics - {keyword[5:].upper()}"
        elif keyword.startswith("stat."):
            return f"Statistics - {keyword[5:].upper()}"
        elif keyword.startswith("econ."):
            return f"Economics - {keyword[5:].upper()}"
        elif keyword.startswith("q-bio."):
            return f"Quantitative Biology - {keyword[6:].upper()}"
        
        return ""

    def _analyze_subject_distribution(self, keywords: List[Dict[str, Any]]) -> List[tuple]:
        subject_counts = {}
        
        for kw_data in keywords:
            keyword = kw_data.get('keyword', '')
            if '.' in keyword:
                subject = keyword.split('.')[0]
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        subject_names = {
            'cs': 'Computer Science',
            'physics': 'Physics',
            'math': 'Mathematics',
            'stat': 'Statistics',
            'econ': 'Economics',
            'q-bio': 'Quantitative Biology'
        }
        
        result = []
        for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
            friendly_name = subject_names.get(subject, subject.upper())
            result.append((friendly_name, count))
        
        return result