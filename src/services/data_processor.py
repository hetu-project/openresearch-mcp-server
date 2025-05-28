import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from ..models.data_models import Paper, Author, SearchResult, SearchMetadata

logger = structlog.get_logger()

class DataProcessor:
    """数据处理服务 - MVP版本"""
    
    def __init__(self):
        pass
    
    async def process_search_result(
        self, 
        raw_data: Dict[str, Any],
        query: str,
        search_params: Dict[str, Any]
    ) -> SearchResult:
        """处理搜索结果"""
        start_time = datetime.now()
        
        try:
            # 解析论文数据
            papers = await self._parse_papers(raw_data.get("papers", []))
            
            # 生成元数据
            metadata = self._generate_metadata(
                raw_data, query, search_params, start_time
            )
            
            # 构建结果
            result = SearchResult(
                papers=papers,
                metadata=metadata
            )
            
            logger.info(
                "Search result processed successfully",
                paper_count=len(papers),
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to process search result", error=str(e))
            raise
    
    async def _parse_papers(self, raw_papers: List[Dict[str, Any]]) -> List[Paper]:
        """解析论文数据"""
        papers = []
        
        for raw_paper in raw_papers:
            try:
                # 解析作者信息
                authors = []
                for raw_author in raw_paper.get("authors", []):
                    author = self._parse_author(raw_author)
                    authors.append(author)
                
                # 解析论文信息
                paper = Paper(
                    id=raw_paper["id"],
                    title=raw_paper["title"],
                    abstract=raw_paper.get("abstract"),
                    authors=authors,
                    publication_date=self._parse_date(raw_paper.get("publication_date")),
                    venue=raw_paper.get("venue"),
                    venue_type=raw_paper.get("venue_type"),
                    doi=raw_paper.get("doi"),
                    arxiv_id=raw_paper.get("arxiv_id"),
                    url=raw_paper.get("url"),
                    keywords=raw_paper.get("keywords", []),
                    language=raw_paper.get("language", "en"),
                    citation_count=raw_paper.get("citation_count"),
                    download_count=raw_paper.get("download_count"),
                )
                
                papers.append(paper)
                
            except Exception as e:
                logger.warning(
                    "Failed to parse paper",
                    paper_id=raw_paper.get("id"),
                    error=str(e)
                )
                continue
        
        return papers
    
    def _parse_author(self, raw_author: Dict[str, Any]) -> Author:
        """解析作者数据"""
        return Author(
            id=raw_author["id"],
            name=raw_author["name"],
            email=raw_author.get("email"),
            orcid=raw_author.get("orcid"),
            affiliations=raw_author.get("affiliations", []),
            h_index=raw_author.get("h_index"),
            citation_count=raw_author.get("citation_count"),
            paper_count=raw_author.get("paper_count"),
            research_interests=raw_author.get("research_interests", [])
        )
    
    def _generate_metadata(
        self,
        raw_data: Dict[str, Any],
        query: str,
        search_params: Dict[str, Any],
        start_time: datetime
    ) -> SearchMetadata:
        """生成搜索元数据"""
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SearchMetadata(
            total_count=raw_data.get("total_count", 0),
            page=search_params.get("page", 1),
            page_size=search_params.get("limit", 20),
            execution_time_ms=execution_time_ms,
            query=query,
            filters_applied=search_params.get("filters", {})
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败，尝试ISO格式
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning("Failed to parse date", date_str=date_str, error=str(e))
            return None