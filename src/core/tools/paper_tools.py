# src/mcp/tools/paper_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class PaperTools(BaseTools):
    """论文相关工具 - MVP版本 - 支持JSON格式返回"""
    
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
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["query"]
                }
            ),
        Tool(
            name="get_paper_details",
            description="根据论文标题获取指定论文的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "titles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "论文标题列表，支持完整标题或部分标题"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "json"],
                        "default": "markdown",
                        "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                    }
                },
                "required": ["titles"]
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
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["paper_id"]
                }
            )
        ]
    
    @handle_tool_error
    async def search_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索论文工具 - 支持JSON格式"""
        query = arguments["query"]
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "markdown")

        logger.info("Searching papers", query=query, filters=filters, format=return_format)
        
        try:
            raw_result = await self.go_client.search_papers(
                query=query,
                filters=filters,
                limit=limit
            )
            
            if return_format == "json":
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_search_result(raw_result, query)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            error_content = self._format_error_response(str(e), "论文搜索")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_paper_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取论文详情工具 - 根据标题搜索"""
        titles = arguments["titles"]
        return_format = arguments.get("format", "markdown")
        
        logger.info("Getting paper details by titles", titles=titles, format=return_format)
        
        try:
            # 使用标题搜索来获取论文详情
            all_papers = []
            
            for title in titles:
                # 对每个标题进行搜索
                search_result = await self.go_client.search_papers(
                    query=title,
                    limit=5  # 限制结果数量，通常第一个结果就是目标论文
                )
                
                papers = search_result.get("papers", [])
                if papers:
                    # 寻找最匹配的论文（标题完全匹配或最相似）
                    best_match = self._find_best_title_match(title, papers)
                    if best_match:
                        all_papers.append(best_match)
                    else:
                        # 如果没有找到完全匹配，取第一个结果
                        all_papers.append(papers[0])
            
            # 构造返回结果
            result = {"papers": all_papers}
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_paper_details(result)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取论文详情")
            return [TextContent(type="text", text=error_content)]
    
    def _find_best_title_match(self, target_title: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """找到标题最匹配的论文"""
        target_lower = target_title.lower().strip()
        
        # 首先寻找完全匹配
        for paper in papers:
            paper_title = paper.get('title', '').lower().strip()
            if paper_title == target_lower:
                return paper
        
        # 如果没有完全匹配，寻找包含关系
        for paper in papers:
            paper_title = paper.get('title', '').lower().strip()
            if target_lower in paper_title or paper_title in target_lower:
                return paper
        
        # 如果都没有匹配，返回第一个
        return papers[0] if papers else None

    @handle_tool_error
    async def get_paper_citations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取论文引用工具 - 支持JSON格式"""
        paper_id = arguments["paper_id"]
        return_format = arguments.get("format", "markdown")
        
        logger.info("Getting paper citations", paper_id=paper_id, format=return_format)
        
        try:
            raw_result = await self.go_client.get_paper_citations(paper_id)
            
            if return_format == "json":
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_citations(raw_result, paper_id)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get paper citations failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取论文引用")
            return [TextContent(type="text", text=error_content)]
    
    # ... 保留所有现有的格式化方法 ...
    
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
            return "❌ 未找到论文详情。"
        
        content = "# 📄 论文详情\n\n"
        
        for paper in papers:
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"## {title}\n\n"
            
            # 基本信息
            content += "### 📋 基本信息\n"
            content += f"**论文ID**: `{self._safe_get_str(paper, 'id', 'N/A')}`\n"
            content += self._format_paper_basic_info(paper)
            
            # 作者信息
            authors = paper.get('authors', [])
            if authors:
                content += f"\n### 👥 作者信息 ({len(authors)} 位)\n"
                for j, author in enumerate(authors, 1):
                    author_name = self._safe_get_str(author, 'name', 'Unknown')
                    author_id = self._safe_get_str(author, 'id')
                    content += f"{j}. **{author_name}**"
                    if author_id:
                        content += f" (ID: `{author_id}`)"
                    content += "\n"
            
            # 影响力指标
            content += "\n### 📊 影响力指标\n"
            citations = self._safe_get_int(paper, 'citations')
            references_count = self._safe_get_int(paper, 'references_count')
            likes_count = self._safe_get_int(paper, 'likes_count')
            
            content += f"**引用数**: {citations}\n"
            content += f"**参考文献数**: {references_count}\n"
            content += f"**点赞数**: {likes_count}\n"
            
            # 关键词
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"\n**关键词**: {self._format_keywords(keywords, max_count=10)}\n"
            
            # 摘要
            abstract = self._safe_get_str(paper, 'abstract')
            if abstract:
                content += f"\n### 📝 摘要\n{abstract}\n"
            
            # 链接和资源
            content += "\n### 🔗 链接和资源\n"
            content += self._format_paper_links(paper)
            
            # 预览图
            img_url = self._safe_get_str(paper, 'img_url')
            if img_url:
                content += f"- [📸 论文预览图]({img_url})\n"
            
            # 用户交互信息
            interaction_info = self._format_user_interaction(paper)
            if interaction_info.strip():
                content += f"\n### 👤 用户交互\n{interaction_info}"
            
            content += "\n---\n\n"
        
        return content

    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        """格式化论文基本信息"""
        info = ""
        
        # 发表时间 - 处理 Unix 时间戳
        published_at = paper.get('published_at')
        if published_at:
            try:
                if isinstance(published_at, (int, float)):
                    # Unix 时间戳
                    from datetime import datetime
                    dt = datetime.fromtimestamp(published_at)
                    formatted_date = dt.strftime('%Y年%m月%d日')
                else:
                    # 字符串格式
                    formatted_date = self._format_date(str(published_at))
                info += f"**发表时间**: {formatted_date}\n"
            except:
                info += f"**发表时间**: {published_at}\n"
        
        # 期刊/会议
        venue_name = self._safe_get_str(paper, 'venue_name')
        venue_id = self._safe_get_str(paper, 'venue_id')
        if venue_name:
            info += f"**发表于**: {venue_name}"
            if venue_id and venue_id != venue_name:
                info += f" ({venue_id})"
            info += "\n"
        elif venue_id:
            info += f"**发表于**: {venue_id}\n"
        
        return info

    def _format_paper_links(self, paper: Dict[str, Any]) -> str:
        """格式化论文链接信息"""
        links = []
        
        # 论文链接
        url = self._safe_get_str(paper, 'url')
        if url:
            if 'arxiv.org' in url:
                links.append(f"- [📄 arXiv 论文]({url})")
            elif 'ieee' in url.lower():
                links.append(f"- [📄 IEEE 论文]({url})")
            else:
                links.append(f"- [📄 论文链接]({url})")
        
        # DOI
        doi = self._safe_get_str(paper, 'doi')
        if doi:
            if doi.startswith('10.'):
                doi_url = f"https://doi.org/{doi}"
                links.append(f"- [🔗 DOI]({doi_url}) (`{doi}`)")
            else:
                links.append(f"- **DOI**: `{doi}`")
        
        return "\n".join(links) + "\n" if links else ""

    def _format_user_interaction(self, paper: Dict[str, Any]) -> str:
        """格式化用户交互信息"""
        info = ""
        
        is_favorited = paper.get('is_favorited_by_user', False)
        is_liked = paper.get('is_liked_by_user', False)
        likes_count = self._safe_get_int(paper, 'likes_count')
        
        if is_favorited or is_liked or likes_count > 0:
            interaction_parts = []
            
            if is_favorited:
                interaction_parts.append("⭐ 已收藏")
            
            if is_liked:
                interaction_parts.append("👍 已点赞")
            
            if likes_count > 0:
                interaction_parts.append(f"💖 {likes_count} 人点赞")
            
            if interaction_parts:
                info += f"**状态**: {' | '.join(interaction_parts)}\n"
        
        return info

    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        """格式化关键词"""
        if not keywords:
            return "无"
        
        # 限制显示数量
        display_keywords = keywords[:max_count]
        keyword_text = ", ".join(f"`{kw}`" for kw in display_keywords)
        
        if len(keywords) > max_count:
            keyword_text += f" 等 {len(keywords)} 个"
        
        return keyword_text

    def _truncate_text(self, text: str, max_length: int = 150) -> str:
        """截断文本"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rstrip() + "..."

    def _format_date(self, date_str: str) -> str:
        """格式化日期字符串"""
        if not date_str:
            return "未知"
        
        try:
            from datetime import datetime
            # 处理多种日期格式
            if 'T' in date_str:
                # ISO 格式
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # 简单日期格式
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.strftime('%Y年%m月%d日')
        except:
            # 如果解析失败，返回原始字符串
            return date_str

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

    def _format_empty_result(self, query: str, entity_type: str) -> str:
        """格式化空结果"""
        return f"❌ 未找到与 '{query}' 相关的{entity_type}。\n\n💡 建议：\n- 检查拼写\n- 尝试使用不同的关键词\n- 使用更通用的搜索词"

    def _format_list_header(self, title: str, count: int, query: str) -> str:
        """格式化列表头部"""
        return f"# {title}\n\n**搜索词**: {query}\n**找到结果**: {count} 个\n\n"

    def _format_error_response(self, error: str, operation: str) -> str:
        """格式化错误响应"""
        return f"❌ {operation}失败\n\n**错误信息**: {error}\n\n💡 请稍后重试或联系管理员。"
    
    def _format_citations(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """格式化引用关系 - 根据实际API返回数据调整"""
        content = f"# 📊 论文引用关系分析\n\n"
        
        # 基本信息
        title = self._safe_get_str(raw_result, 'title')
        doi = self._safe_get_str(raw_result, 'doi')
        url = self._safe_get_str(raw_result, 'url')
        
        content += f"**论文ID**: `{paper_id}`\n"
        if title:
            content += f"**论文标题**: {title}\n"
        if doi:
            content += f"**DOI**: {doi}\n"
        if url:
            content += f"**链接**: {url}\n"
        
        # 引用统计
        content += "\n## 📈 引用统计\n"
        outgoing = self._safe_get_int(raw_result, 'outgoing_citations_count')
        incoming = self._safe_get_int(raw_result, 'incoming_citations_count')
        total = self._safe_get_int(raw_result, 'total_citations_count')
        
        content += f"- **引用其他论文**: {outgoing} 篇\n"
        content += f"- **被其他论文引用**: {incoming} 篇\n"
        content += f"- **总引用关系**: {total} 条\n\n"
        
        # 被引用论文 (citing_papers)
        citing_papers = raw_result.get('citing_papers', [])
        if citing_papers:
            content += f"## 📄 引用本文的论文 ({len(citing_papers)} 篇)\n\n"
            for i, paper in enumerate(citing_papers, 1):
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                doi = self._safe_get_str(paper, 'doi')
                url = self._safe_get_str(paper, 'url')
                paper_id = self._safe_get_str(paper, 'id')
                
                content += f"### {i}. {title}\n\n"
                content += f"**论文ID**: `{paper_id}`\n"
                
                if citations > 0:
                    content += f"**引用数**: {citations}\n"
                
                if cited_at:
                    try:
                        # 处理 ISO 格式时间
                        from datetime import datetime
                        dt = datetime.fromisoformat(cited_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y年%m月%d日')
                        content += f"**引用时间**: {formatted_date}\n"
                    except:
                        content += f"**引用时间**: {cited_at}\n"
                
                if doi:
                    content += f"**DOI**: {doi}\n"
                
                if url:
                    content += f"**链接**: {url}\n"
                
                # 关键词
                keywords = paper.get('keywords', [])
                if keywords and keywords != [""]:  # 过滤空关键词
                    valid_keywords = [kw for kw in keywords if kw.strip()]
                    if valid_keywords:
                        content += f"**关键词**: {', '.join(f'`{kw}`' for kw in valid_keywords)}\n"
                
                content += "\n---\n\n"
        else:
            content += "## 📄 引用本文的论文\n\n❌ 暂无其他论文引用本文。\n\n"
        
        # 引用的论文 (cited_papers)
        cited_papers = raw_result.get('cited_papers', [])
        if cited_papers:
            content += f"## 📚 本文引用的论文 ({len(cited_papers)} 篇)\n\n"
            for i, paper in enumerate(cited_papers, 1):
                title = self._safe_get_str(paper, 'title', 'Unknown Title')
                citations = self._safe_get_int(paper, 'citations')
                cited_at = self._safe_get_str(paper, 'cited_at')
                doi = self._safe_get_str(paper, 'doi')
                url = self._safe_get_str(paper, 'url')
                paper_id = self._safe_get_str(paper, 'id')
                
                content += f"### {i}. {title}\n\n"
                content += f"**论文ID**: `{paper_id}`\n"
                
                if citations > 0:
                    content += f"**引用数**: {citations}\n"
                
                if cited_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(cited_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y年%m月%d日')
                        content += f"**引用时间**: {formatted_date}\n"
                    except:
                        content += f"**引用时间**: {cited_at}\n"
                
                if doi:
                    content += f"**DOI**: {doi}\n"
                
                if url:
                    content += f"**链接**: {url}\n"
                
                # 关键词
                keywords = paper.get('keywords', [])
                if keywords and keywords != [""]:
                    valid_keywords = [kw for kw in keywords if kw.strip()]
                    if valid_keywords:
                        content += f"**关键词**: {', '.join(f'`{kw}`' for kw in valid_keywords)}\n"
                
                content += "\n---\n\n"
        else:
            content += "## 📚 本文引用的论文\n\n❌ 本文未引用其他论文。\n\n"
        
        # 添加分析总结
        content += "## 🔍 引用分析总结\n\n"
        
        if incoming > 0:
            content += f"✅ 本文被 **{incoming}** 篇论文引用，显示了一定的学术影响力。\n"
        else:
            content += "📝 本文尚未被其他论文引用。\n"
        
        if outgoing > 0:
            content += f"📚 本文引用了 **{outgoing}** 篇相关论文，体现了良好的文献基础。\n"
        else:
            content += "📝 本文未引用其他论文。\n"
        
        return content
