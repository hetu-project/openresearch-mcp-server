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
    async def search_authors(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """搜索作者工具 - 支持姓名和ID搜索"""
        query = arguments.get("query")
        author_id = arguments.get("author_id")
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        return_format = arguments.get("format", "markdown")

        if not query and not author_id:
            return [TextContent(type="text", text="❌ 请提供查询条件（姓名或ID）")]

        logger.info("Searching authors", query=query, author_id=author_id, filters=filters, format=return_format)
        
        try:
            raw_result = await self.go_client.search_authors(
                query=query,
                author_id=author_id,
                filters=filters,
                limit=limit
            )
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 根据搜索类型选择格式化方法
                if author_id:
                    content = self._format_author_details(raw_result)
                else:
                    content = self._format_author_search_result(raw_result, query)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            error_content = self._format_error_response(str(e), "作者搜索")
            return [TextContent(type="text", text=error_content)]
    
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
    
    # 格式化方法保持不变...
    def _format_author_search_result(self, raw_result: Dict[str, Any], query: str) -> str:
        """格式化作者搜索结果"""
        authors = raw_result.get("authors", [])
        count = raw_result.get("count", len(authors))
        
        if not authors:
            return self._format_empty_result(query, "作者")
        
        content = self._format_list_header("作者搜索结果", count, query)
        
        for i, author in enumerate(authors, 1):
            name = self._safe_get_str(author, 'name', 'Unknown Author')
            content += f"## {i}. {name}\n\n"
            
            # 基本信息
            content += self._format_author_basic_info(author)
            
            # 研究兴趣
            interests = author.get('research_interests')
            if interests:
                content += f"**研究兴趣**: {', '.join(interests)}\n"
            
            # 邮箱
            email = self._safe_get_str(author, 'email')
            if email:
                content += f"**邮箱**: {email}\n"
            
            # 合作者信息
            coauthors = author.get('coauthors', [])
            if coauthors:
                content += f"**主要合作者**: {len(coauthors)} 位\n"
                # 显示前3位合作者
                for j, coauthor in enumerate(coauthors[:3], 1):
                    coauthor_name = self._safe_get_str(coauthor, 'name')
                    collaboration_count = self._safe_get_int(coauthor, 'collaboration_count')
                    if coauthor_name:
                        content += f"  {j}. {coauthor_name}"
                        if collaboration_count > 0:
                            content += f" (合作{collaboration_count}次)"
                        content += "\n"
            
            # 作者ID
            content += f"**ID**: {self._safe_get_str(author, 'id', 'N/A')}\n"
            content += "\n---\n\n"
        
        return content
    
    def _format_author_details(self, raw_result: Dict[str, Any]) -> str:
        """格式化作者详情"""
        if not raw_result:
            return "❌ 未收到任何数据"
        
        authors = raw_result.get("authors", [])
        if not authors:
            return "❌ 未找到作者信息"
        
        content_parts = []
        
        for i, author in enumerate(authors, 1):
            author_info = []
            author_info.append(f"# 👤 作者详情 {i}")
            author_info.append("")
            
            # 基本信息
            author_info.append(f"## 基本信息")
            author_info.append(f"**姓名**: {self._safe_get_str(author, 'name', 'Unknown')}")
            author_info.append(f"**ID**: `{self._safe_get_str(author, 'id', 'N/A')}`")
            author_info.append(f"**机构**: {self._safe_get_str(author, 'affiliation', 'N/A')}")
            
            email = self._safe_get_str(author, 'email')
            if email:
                author_info.append(f"**邮箱**: {email}")
            
            # 学术指标
            author_info.append("")
            author_info.append(f"## 📊 学术指标")
            author_info.append(f"**论文数量**: {self._safe_get_int(author, 'paper_count')} 篇")
            author_info.append(f"**引用数量**: {self._safe_get_int(author, 'citation_count')} 次")
            author_info.append(f"**H-index**: {self._safe_get_int(author, 'h_index')}")
            
            # 研究兴趣
            interests = author.get('research_interests')
            if interests:
                author_info.append("")
                author_info.append(f"## 🔬 研究兴趣")
                if isinstance(interests, list):
                    author_info.append(f"{', '.join(interests)}")
                else:
                    author_info.append(f"{interests}")
            
            # 合作者信息
            coauthors = author.get('coauthors', [])
            if coauthors:
                author_info.append("")
                author_info.append(f"## 🤝 合作网络 ({len(coauthors)} 位合作者)")
                
                # 按合作次数排序
                sorted_coauthors = sorted(
                    coauthors, 
                    key=lambda x: self._safe_get_int(x, 'collaboration_count'), 
                    reverse=True
                )
                
                for j, coauthor in enumerate(sorted_coauthors[:10], 1):  # 显示前10位
                    collab_count = self._safe_get_int(coauthor, 'collaboration_count')
                    coauthor_name = self._safe_get_str(coauthor, 'name', 'Unknown')
                    coauthor_id = self._safe_get_str(coauthor, 'id', 'N/A')
                    
                    author_info.append(f"{j:2d}. **{coauthor_name}** - {collab_count}次合作")
                    author_info.append(f"     ID: `{coauthor_id}`")
                    
                    affiliation = self._safe_get_str(coauthor, 'affiliation')
                    if affiliation:
                        author_info.append(f"     机构: {affiliation}")
                    author_info.append("")  # 添加空行分隔
                
                if len(coauthors) > 10:
                    author_info.append(f"... 还有 {len(coauthors) - 10} 位合作者")
            
            content_parts.append("\n".join(author_info))
        
        # 添加总结信息
        summary = f"📊 **查询结果**: 找到 {len(authors)} 位作者的详细信息\n"
        return summary + "\n" + ("\n" + "="*60 + "\n").join(content_parts)
    
    
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


