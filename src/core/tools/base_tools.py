from typing import Dict, Any, List
import structlog
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor

logger = structlog.get_logger()

class BaseTools:
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
    def _format_authors_list(self, authors: List[Any], max_count: int = 3) -> str:
        if not authors:
            return "Unknown Author"
        
        try:
            if isinstance(authors[0], dict):
                author_names = [author.get('name', 'Unknown') for author in authors[:max_count]]
            else:
                author_names = [str(author) for author in authors[:max_count]]
            
            result = ", ".join(author_names)
            if len(authors) > max_count:
                result += f" etc ({len(authors)} authors)"
            
            return result
            
        except Exception as e:
            logger.warning("Failed to format authors list", error=str(e))
            return "Failed to parse author information"
    
    def _format_date(self, date_str: str) -> str:
        if not date_str:
            return "Unknown Time"
        
        try:
            return date_str[:10]
        except Exception:
            return str(date_str)
    
    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        if not text:
            return ""
        
        text = str(text).strip()
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    def _format_keywords(self, keywords: List[str], max_count: int = 5) -> str:
        if not keywords:
            return "No Keywords"
        
        try:
            selected_keywords = keywords[:max_count]
            result = ", ".join(selected_keywords)
            
            if len(keywords) > max_count:
                result += f" etc ({len(keywords)} keywords)"
            
            return result
            
        except Exception as e:
            logger.warning("Failed to format keywords", error=str(e))
            return "Failed to parse keywords"
    
    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        try:
            value = data.get(key, default)
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _safe_get_str(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        try:
            value = data.get(key, default)
            return str(value) if value is not None else default
        except Exception:
            return default
    
    def _format_paper_basic_info(self, paper: Dict[str, Any]) -> str:
        content = ""
        
        title = self._safe_get_str(paper, 'title', 'Unknown Title')
        content += f"**Title**: {title}\n"
        
        authors = paper.get('authors', [])
        content += f"**Authors**: {self._format_authors_list(authors)}\n"
        
        published_at = self._safe_get_str(paper, 'published_at')
        content += f"**Published At**: {self._format_date(published_at)}\n"
        
        citations = self._safe_get_int(paper, 'citations')
        if citations > 0:
            content += f"**Citations**: {citations}\n"
        
        venue = self._safe_get_str(paper, 'venue_name')
        if venue:
            content += f"**Published In**: {venue}\n"
        
        return content
    
    def _format_author_basic_info(self, author: Dict[str, Any]) -> str:
        content = ""
        
        name = self._safe_get_str(author, 'name', 'Unknown Author')
        content += f"**Name**: {name}\n"
        
        affiliation = self._safe_get_str(author, 'affiliation')
        if affiliation:
            content += f"**Affiliation**: {affiliation}\n"
        
        paper_count = self._safe_get_int(author, 'paper_count')
        if paper_count > 0:
            content += f"**Paper Count**: {paper_count}\n"
        
        citation_count = self._safe_get_int(author, 'citation_count')
        if citation_count > 0:
            content += f"**Total Citations**: {citation_count}\n"
        
        h_index = self._safe_get_int(author, 'h_index')
        if h_index > 0:
            content += f"**H-index**: {h_index}\n"
        
        return content
    
    def _format_error_response(self, error_msg: str, context: str = "") -> str:
        content = "# Operation Failed\n\n"
        if context:
            content += f"**Operation**: {context}\n"
        content += f"**Error**: {error_msg}\n\n"
        content += "Please check input parameters or try again later.\n"
        return content
    
    def _format_empty_result(self, query: str, result_type: str = "results") -> str:
        content = f"# Search Results\n\n"
        content += f"**Query**: {query}\n"
        content += f"**Results**: No related {result_type} found\n\n"
        content += "Suggestions:\n"
        content += "- Try different keywords\n"
        content += "- Check spelling\n"
        content += "- Use more general search terms\n"
        return content
    
    def _get_trend_indicator(self, current: int, previous: int) -> str:
        if previous == 0:
            return "🆕"
        elif current > previous:
            return "↗"
        elif current < previous:
            return "↘"
        else:
            return "→"
    
    def _format_list_header(self, title: str, total_count: int, query: str = "") -> str:
        content = f"# {title}\n\n"
        if query:
            content += f"**Query**: {query}\n"
        content += f"**Total**: {total_count}\n\n"
        return content