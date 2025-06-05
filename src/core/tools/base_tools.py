# src/mcp/tools/base_tools.py
from typing import Dict, Any, List
import structlog
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor

logger = structlog.get_logger()

class BaseTools:
    """工具基类 - MVP版本，提供公共方法"""
    
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
    def _format_authors_list(self, authors: List[Any], max_count: int = 3) -> str:
        """格式化作者列表"""
        if not authors:
            return "未知作者"
        
        try:
            # 处理字典格式的作者
            if isinstance(authors[0], dict):
                author_names = [author.get('name', 'Unknown') for author in authors[:max_count]]
            else:
                # 处理字符串格式的作者
                author_names = [str(author) for author in authors[:max_count]]
            
            result = ", ".join(author_names)
            if len(authors) > max_count:
                result += f" 等 ({len(authors)}位作者)"
            
            return result
            
        except Exception as e:
            logger.warning("Failed to format authors list", error=str(e))
            return "作者信息解析失败"
    
    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return "未知时间"
        
        try:
            # 只取日期部分 (YYYY-MM-DD)
            return date_str[:10]
        except Exception:
            return str(date_str)
    
    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        """截断文本"""
        if not text:
            return ""
        
        text = str(text).strip()
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        """格式化关键词列表"""
        if not keywords:
            return "无关键词"
        
        try:
            # 取前几个关键词
            selected_keywords = keywords[:max_count]
            result = ", ".join(selected_keywords)
            
            if len(keywords) > max_count:
                result += f" 等 ({len(keywords)}个关键词)"
            
            return result
            
        except Exception as e:
            logger.warning("Failed to format keywords", error=str(e))
            return "关键词解析失败"
    
    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        """安全获取整数值"""
        try:
            value = data.get(key, default)
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _safe_get_str(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        """安全获取字符串值"""
        try:
            value = data.get(key, default)
            return str(value) if value is not None else default
        except Exception:
            return default
    
    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        """格式化论文基本信息"""
        content = ""
        
        # 标题
        title = self._safe_get_str(paper, 'title', 'Unknown Title')
        content += f"**标题**: {title}\n"
        
        # 作者
        authors = paper.get('authors', [])
        content += f"**作者**: {self._format_authors_list(authors)}\n"
        
        # 发表时间
        published_at = self._safe_get_str(paper, 'published_at')
        content += f"**发表时间**: {self._format_date(published_at)}\n"
        
        # 引用数
        citations = self._safe_get_int(paper, 'citations')
        if citations > 0:
            content += f"**引用数**: {citations}\n"
        
        # 会议/期刊
        venue = self._safe_get_str(paper, 'venue_name')
        if venue:
            content += f"**发表于**: {venue}\n"
        
        return content
    
    def _format_author_basic_info(self, author: Dict[str, Any]) -> str:
        """格式化作者基本信息"""
        content = ""
        
        # 姓名
        name = self._safe_get_str(author, 'name', 'Unknown Author')
        content += f"**姓名**: {name}\n"
        
        # 机构
        affiliation = self._safe_get_str(author, 'affiliation')
        if affiliation:
            content += f"**机构**: {affiliation}\n"
        
        # 论文数
        paper_count = self._safe_get_int(author, 'paper_count')
        if paper_count > 0:
            content += f"**论文数**: {paper_count}\n"
        
        # 引用数
        citation_count = self._safe_get_int(author, 'citation_count')
        if citation_count > 0:
            content += f"**总引用数**: {citation_count}\n"
        
        # H指数
        h_index = self._safe_get_int(author, 'h_index')
        if h_index > 0:
            content += f"**H指数**: {h_index}\n"
        
        return content
    
    def _format_error_response(self, error_msg: str, context: str = "") -> str:
        """格式化错误响应"""
        content = "# 操作失败\n\n"
        if context:
            content += f"**操作**: {context}\n"
        content += f"**错误**: {error_msg}\n\n"
        content += "请检查输入参数或稍后重试。\n"
        return content
    
    def _format_empty_result(self, query: str, result_type: str = "结果") -> str:
        """格式化空结果"""
        content = f"# 搜索结果\n\n"
        content += f"**查询**: {query}\n"
        content += f"**结果**: 未找到相关{result_type}\n\n"
        content += "建议：\n"
        content += "- 尝试使用不同的关键词\n"
        content += "- 检查拼写是否正确\n"
        content += "- 使用更通用的搜索词\n"
        return content
    
    def _get_trend_indicator(self, current: int, previous: int) -> str:
        """获取趋势指示器"""
        if previous == 0:
            return "🆕"
        elif current > previous:
            return "↗"
        elif current < previous:
            return "↘"
        else:
            return "→"
    
    def _format_list_header(self, title: str, total_count: int, query: str = "") -> str:
        """格式化列表头部"""
        content = f"# {title}\n\n"
        if query:
            content += f"**查询**: {query}\n"
        content += f"**总数**: {total_count}\n\n"
        return content
