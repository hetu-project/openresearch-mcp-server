# src/core/tools/author_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class AuthorTools(BaseTools):
    """作者相关工具 - 支持JSON格式返回"""
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="search_authors",
                description="搜索学术作者，支持姓名、机构、研究领域等过滤条件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询，支持作者姓名"
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
                name="get_author_papers",
                description="获取作者发表的论文列表",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "作者ID"
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
                    "required": ["author_id"]
                }
            )
        ]

    
    @handle_tool_error
    async def get_author_papers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取作者论文工具 - 支持JSON格式"""
        author_id = arguments["author_id"]
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "markdown")
        
        logger.info("Getting author papers", author_id=author_id, limit=limit, format=return_format)
        
        try:
            raw_result = await self.go_client.get_author_papers(author_id)
            
            if return_format == "json":
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_author_papers(raw_result, author_id, limit)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get author papers failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取作者论文")
            return [TextContent(type="text", text=error_content)]
    
    
    def _format_author_papers(self, raw_result: Dict[str, Any], author_id: str, limit: int) -> str:
        """格式化作者论文"""
        papers = raw_result.get("papers", [])
        count = raw_result.get("count", len(papers))
        
        content = f"# 📄 作者发表论文\n\n"
        content += f"**作者ID**: `{author_id}`\n"
        content += f"**论文总数**: {count} 篇\n"
        content += f"**显示数量**: {len(papers)} 篇\n\n"
        
        if not papers:
            content += "❌ 该作者暂无论文记录。\n"
            return content
        
        content += f"## 📋 论文列表\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = self._safe_get_str(paper, 'title', 'Unknown Title')
            content += f"### {i}. {title}\n\n"
            
            # 论文ID
            paper_id = self._safe_get_str(paper, 'id')
            if paper_id:
                content += f"**论文ID**: `{paper_id}`\n"
            
            # 发表时间
            published_at = self._safe_get_str(paper, 'published_at')
            if published_at:
                # 格式化日期显示
                try:
                    from datetime import datetime
                    # 解析 ISO 格式时间
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y年%m月%d日')
                    content += f"**发表时间**: {formatted_date}\n"
                except:
                    content += f"**发表时间**: {published_at}\n"
            
            # 作者顺序
            author_order = self._safe_get_int(paper, 'author_order')
            if author_order > 0:
                # 添加序数词
                if author_order == 1:
                    order_text = "第一作者"
                elif author_order == 2:
                    order_text = "第二作者"
                elif author_order == 3:
                    order_text = "第三作者"
                else:
                    order_text = f"第{author_order}作者"
                content += f"**作者顺序**: {order_text}\n"
            
            # 是否通讯作者
            is_corresponding = paper.get('is_corresponding')
            if is_corresponding:
                content += f"**通讯作者**: ✅ 是\n"
            else:
                content += f"**通讯作者**: ❌ 否\n"
            
            content += "\n---\n\n"
        
        # 添加统计信息
        if count > len(papers):
            content += f"💡 **提示**: 该作者共有 {count} 篇论文，当前显示前 {len(papers)} 篇。\n\n"
        
        # 添加作者顺序统计
        first_author_count = sum(1 for p in papers if p.get('author_order') == 1)
        corresponding_count = sum(1 for p in papers if p.get('is_corresponding'))
        
        content += f"## 📊 统计信息\n\n"
        content += f"- **第一作者论文**: {first_author_count} 篇\n"
        content += f"- **通讯作者论文**: {corresponding_count} 篇\n"
        
        # 按年份统计
        year_stats = {}
        for paper in papers:
            published_at = paper.get('published_at', '')
            if published_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    year = dt.year
                    year_stats[year] = year_stats.get(year, 0) + 1
                except:
                    pass
        
        if year_stats:
            content += f"- **按年份分布**:\n"
            for year in sorted(year_stats.keys(), reverse=True):
                content += f"  - {year}年: {year_stats[year]} 篇\n"
        
        return content


    # 修改 search_authors 方法中的格式化逻辑
    @handle_tool_error
    async def search_authors(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索作者工具 - 支持姓名和ID搜索"""
        query = arguments.get("query")
        author_id = arguments.get("author_id")
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "json")

        if not query and not author_id:
            return [TextContent(type="text", text="❌ 请提供查询条件（姓名或ID）")]

        logger.info("Searching authors IN AUTHOR TOOL", query=query, author_id=author_id, filters=filters, format=return_format)
        
        try:
            raw_result = await self.go_client.search_authors(
                query=query,
                author_id=author_id,
                filters=filters,
                limit=limit
            )
            
            if return_format == "json":
                json_str = json.dumps(raw_result, ensure_ascii=False, indent=2)
                logger.debug("Returning JSON format", json_data=json_str)
                return [TextContent(type="text", text=json_str)]
            else:
                # 构建搜索条件描述
                if query:
                    search_term = str(query)
                elif author_id:
                    search_term = f"ID: {str(author_id)}"
                else:
                    search_term = "未知查询条件"
                
                content = self._format_authors_result(raw_result, search_term)
                logger.debug("Returning Markdown format", markdown_content=content)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            error_content = self._format_error_response(str(e), "作者搜索")
            return [TextContent(type="text", text=error_content)]

    def _format_authors_result(self, raw_result: Dict[str, Any], search_term: str) -> str:
        """统一的作者结果格式化方法"""
        authors = raw_result.get("authors", [])
        count = raw_result.get("count", len(authors))
        
        if not authors:
            return self._format_empty_result(search_term, "作者")
        
        # 如果只有一个作者，显示详细信息
        if len(authors) == 1:
            return self._format_single_author_details(authors[0], search_term)
        else:
            # 多个作者时显示列表格式
            return self._format_multiple_authors_list(authors, count, search_term)

    def _format_single_author_details(self, author: Dict[str, Any], search_term: str) -> str:
        """格式化单个作者的详细信息"""
        content = f"# 👤 作者详情\n\n"
        content += f"**搜索条件**: {search_term}\n\n"
        
        # 基本信息
        content += f"## 基本信息\n"
        content += f"**姓名**: {self._safe_get_str(author, 'name', 'Unknown')}\n"
        content += f"**ID**: `{self._safe_get_str(author, 'id', 'N/A')}`\n"
        content += f"**机构**: {self._safe_get_str(author, 'affiliation', 'N/A')}\n"
        
        email = self._safe_get_str(author, 'email')
        if email:
            content += f"**邮箱**: {email}\n"
        
        # 学术指标
        content += f"\n## 📊 学术指标\n"
        content += f"**论文数量**: {self._safe_get_int(author, 'paper_count')} 篇\n"
        content += f"**引用数量**: {self._safe_get_int(author, 'citation_count')} 次\n"
        content += f"**H-index**: {self._safe_get_int(author, 'h_index')}\n"
        
        # 研究兴趣
        interests = author.get('research_interests')
        if interests:
            content += f"\n## 🔬 研究兴趣\n"
            if isinstance(interests, list):
                content += f"{', '.join(interests)}\n"
            else:
                content += f"{interests}\n"
        
        # 合作者信息
        coauthors = author.get('coauthors', [])
        if coauthors:
            content += f"\n## 🤝 合作网络 ({len(coauthors)} 位合作者)\n\n"
            
            # 按合作次数排序
            sorted_coauthors = sorted(
                coauthors, 
                key=lambda x: self._safe_get_int(x, 'collaboration_count'), 
                reverse=True
            )
            
            for i, coauthor in enumerate(sorted_coauthors[:10], 1):  # 显示前10位
                collab_count = self._safe_get_int(coauthor, 'collaboration_count')
                coauthor_name = self._safe_get_str(coauthor, 'name', 'Unknown')
                coauthor_id = self._safe_get_str(coauthor, 'id', 'N/A')
                
                content += f"{i:2d}. **{coauthor_name}** - {collab_count}次合作\n"
                content += f"     ID: `{coauthor_id}`\n"
                
                affiliation = self._safe_get_str(coauthor, 'affiliation')
                if affiliation:
                    content += f"     机构: {affiliation}\n"
                content += "\n"
            
            if len(coauthors) > 10:
                content += f"... 还有 {len(coauthors) - 10} 位合作者\n"
        
        return content

    def _format_multiple_authors_list(self, authors: List[Dict[str, Any]], count: int, search_term: str) -> str:
        """格式化多个作者的列表信息"""
        content = self._format_list_header("作者搜索结果", count, search_term)
        
        for i, author in enumerate(authors, 1):
            name = self._safe_get_str(author, 'name', 'Unknown Author')
            content += f"## {i}. {name}\n\n"
            
            # 基本信息
            content += self._format_author_basic_info(author)
            
            # 研究兴趣
            interests = author.get('research_interests')
            if interests:
                if isinstance(interests, list):
                    content += f"**研究兴趣**: {', '.join(interests)}\n"
                else:
                    content += f"**研究兴趣**: {interests}\n"
            
            # 邮箱
            email = self._safe_get_str(author, 'email')
            if email:
                content += f"**邮箱**: {email}\n"
            
            # 合作者信息（简化显示）
            coauthors = author.get('coauthors', [])
            if coauthors:
                content += f"**合作者**: {len(coauthors)} 位"
                # 显示前3位主要合作者
                top_coauthors = sorted(coauthors, key=lambda x: self._safe_get_int(x, 'collaboration_count'), reverse=True)[:3]
                if top_coauthors:
                    names = [self._safe_get_str(c, 'name') for c in top_coauthors if self._safe_get_str(c, 'name')]
                    if names:
                        content += f" (主要: {', '.join(names)})"
                content += "\n"
            
            # 作者ID
            content += f"**ID**: `{self._safe_get_str(author, 'id', 'N/A')}`\n"
            content += "\n---\n\n"
        
        return content
