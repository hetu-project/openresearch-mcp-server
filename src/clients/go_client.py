# src/clients/go_client.py
import asyncio
import aiohttp
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from ..config import settings
from ..utils.error_handler import ServiceConnectionError

logger = structlog.get_logger()

class GoServiceClient:
    """Go服务客户端 - 基于实际API文档"""
    
    def __init__(self):
        self.base_url = settings.go_service_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=settings.go_service_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def connect(self):
        """简化的线程安全连接"""
        if self.session and not self.session.closed:
            return
            
        async with self._session_lock:
            if self.session and not self.session.closed:
                return
            
            old_session = self.session
            new_session = None    
            connector = None

            try:
                connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=30,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
                
                new_session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=self.timeout,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': f'{settings.server_name}/{settings.server_version}'
                    }
                )
                self.session = new_session

                if old_session and not old_session.closed:
                    try:
                        asyncio.create_task(old_session.close())
                    except Exception as e:
                        logger.warning("Failed to close old session", error=str(e))

                logger.info("Go service client connected", base_url=self.base_url)
                
            except Exception as e:
                if connector:
                    try:
                        await connector.close()
                    except Exception:
                        pass
                self.session = None
                logger.error("Failed to create Go service client", error=str(e))
                raise
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Go service client disconnected")
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """确保 session 存在并返回非 None 的 session"""
        if not self.session or self.session.closed:
            await self.connect()
        
        if not self.session:
            raise ServiceConnectionError("Failed to create session")
        
        return self.session
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        session = await self._ensure_session()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(
                "Making request to Go service",
                method=method,
                url=url,
                data=data,
                params=params
            )
            
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(
                        "Go service request failed",
                        status=response.status,
                        error=error_text[:500],
                        url=url
                    )
                    raise ServiceConnectionError(
                        f"Go service request failed: {response.status} - {error_text}"
                    )
                
                try:
                    result = await response.json()
                                    # 添加详细的响应调试
                    print(f"DEBUG: Response status: {response.status}")
                    print(f"DEBUG: Response content: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    logger.debug(
                        "Go service request successful",
                        url=url,
                        response_size=len(str(result))
                    )
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON response", error=str(e))
                    raise ServiceConnectionError(f"Invalid JSON response: {str(e)}")
        
        except aiohttp.ClientError as e:
            logger.error("HTTP client error", error=str(e), url=url)
            raise ServiceConnectionError(f"HTTP client error: {str(e)}")
        
        except asyncio.TimeoutError:
            logger.error("Request timeout", url=url)
            raise ServiceConnectionError(f"Request timeout: {url}")

    # ============ 论文相关接口 ============
    
    async def search_papers(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "relevance",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """搜索论文 - GET /papers"""
        logger.info(
            "Searching papers via Go service",
            query=query,
            filters=filters,
            limit=limit
        )
        
        # 构建查询参数
        params = {}
        if query:
            params["title"] = query
        if filters:
            if filters.get("keywords"):
                params["keywords"] = filters["keywords"]
            if filters.get("author"):
                params["author"] = filters["author"]
            if filters.get("year"):
                params["year"] = filters["year"]
            if filters.get("venue"):
                params["venue"] = filters["venue"]
            if filters.get("doi"):
                params["doi"] = filters["doi"]
        
        params["limit"] = limit
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/papers",
                params=params
            )
            
            logger.info(
                "Paper search completed",
                returned_count=len(result.get("papers", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            raise
    
    async def get_paper_details(self, titles: List[str]) -> Dict[str, Any]:
        """获取论文详情 - 通过标题搜索"""
        logger.info("Getting paper details via titles", titles=titles)
        
        try:
            # 批量获取论文详情
            all_papers = []
            
            for title in titles:
                # 使用标题进行精确搜索
                result = await self._make_request(
                    method="GET",
                    endpoint="/papers",
                    params={"title": title, "limit": 5}
                )
                
                papers = result.get("papers", [])
                if papers:
                    # 返回所有候选论文，让调用方决定如何选择
                    all_papers.extend([{
                        "search_title": title,
                        "candidates": papers
                    }])
            
            logger.info(
                "Paper details retrieved",
                requested_count=len(titles),
                returned_count=len(all_papers)
            )
            
            return {"paper_searches": all_papers}
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            raise

    async def get_paper_citations(self, paper_id: str) -> Dict[str, Any]:
        """获取论文引用关系 - GET /papers/:id/citations"""
        logger.info("Getting paper citations", paper_id=paper_id)
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint=f"/papers/{paper_id}/citations"
            )
            
            # 验证返回数据结构
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            # 确保必要字段存在
            result.setdefault('citing_papers', [])
            result.setdefault('cited_papers', [])
            result.setdefault('incoming_citations_count', len(result.get('citing_papers', [])))
            result.setdefault('outgoing_citations_count', len(result.get('cited_papers', [])))
            result.setdefault('total_citations_count', 
                            result.get('incoming_citations_count', 0) + 
                            result.get('outgoing_citations_count', 0))
            
            logger.info(
                "Paper citations retrieved",
                paper_id=paper_id,
                citing_count=len(result.get("citing_papers", [])),
                cited_count=len(result.get("cited_papers", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get paper citations failed", error=str(e))
            raise
    
    async def get_paper_recommendations(self, paper_id: str) -> Dict[str, Any]:
        """获取论文推荐 - GET /papers/:id/recommendations"""
        logger.info("Getting paper recommendations", paper_id=paper_id)
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint=f"/papers/{paper_id}/recommendations"
            )
            
            logger.info(
                "Paper recommendations retrieved",
                paper_id=paper_id,
                recommendation_count=len(result.get("recommendations", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get paper recommendations failed", error=str(e))
            raise
    
    async def get_trending_papers(
        self,
        time_window: str = "month",
        limit: int = 20
    ) -> Dict[str, Any]:
        """获取热门论文 - GET /papers/trending"""
        logger.info(
            "Getting trending papers",
            time_window=time_window,
            limit=limit
        )
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/papers/trending",
                params={"time": time_window, "limit": limit}
            )
            
            # 验证返回数据结构
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            # 确保必要字段存在
            result.setdefault('trending_papers', [])
            result.setdefault('count', len(result.get('trending_papers', [])))
            result.setdefault('time_window', time_window)
            
            # 验证每篇论文的数据完整性
            papers = result.get('trending_papers', [])
            for paper in papers:
                # 确保基本字段存在
                paper.setdefault('id', '')
                paper.setdefault('title', 'Unknown Title')
                paper.setdefault('abstract', '')
                paper.setdefault('authors', [])
                paper.setdefault('keywords', [])
                paper.setdefault('citations', 0)
                paper.setdefault('popularity_score', 0.0)
                paper.setdefault('published_year', 0)
                paper.setdefault('doi', '')
                paper.setdefault('url', '')
                paper.setdefault('venue_name', '')
                paper.setdefault('venue_id', '')
                paper.setdefault('img_url', '')
            
            logger.info(
                "Trending papers retrieved",
                count=len(result.get("trending_papers", [])),
                time_window=result.get("time_window")
            )
            
            return result
            
        except Exception as e:
            logger.error("Get trending papers failed", error=str(e))
            raise

    
    async def get_top_keywords(self) -> Dict[str, Any]:
        """获取热门话题 - GET /papers/keywords/top"""
        logger.info("Getting top keywords")
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/papers/keywords/top"
            )
            
            # 验证返回数据结构
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            # 确保必要字段存在
            result.setdefault('keywords', [])
            result.setdefault('count', len(result.get('keywords', [])))
            
            # 验证每个关键词的数据完整性
            keywords = result.get('keywords', [])
            for keyword_data in keywords:
                keyword_data.setdefault('keyword', '')
                keyword_data.setdefault('paper_count', 0)
            
            logger.info(
                "Top keywords retrieved",
                count=len(result.get("keywords", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get top keywords failed", error=str(e))
            raise

    # ============ 作者相关接口 ============
    
    async def search_authors(
        self,
        query: Optional[str] = None,
        author_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """搜索作者 - 支持按姓名、ID或其他条件搜索 - GET /authors"""
        logger.info(
            "Searching authors via Go service",
            query=query,
            author_id=author_id,
            filters=filters,
            limit=limit
        )
        
        params = {}
        
        # 按 ID 搜索（优先级最高）
        if author_id:
            params["id"] = author_id
        # 按姓名搜索
        elif query:
            params["name"] = query
        
        # 其他过滤条件
        if filters:
            if filters.get("affiliation"):
                params["affiliation"] = filters["affiliation"]
            if filters.get("research_area"):
                params["interest"] = filters["research_area"]
        
        # 添加 limit（只在非 ID 搜索时使用，因为 ID 搜索通常返回单个结果）
        if not author_id:
            params["limit"] = limit
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/authors",
                params=params
            )
            
            logger.info(
                "Author search completed",
                returned_count=len(result.get("authors", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            raise
    
    async def get_author_papers(self, author_id: str) -> Dict[str, Any]:
        """获取作者发表的论文 - GET /authors/:id/papers"""
        logger.info("Getting author papers", author_id=author_id)
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint=f"/authors/{author_id}/papers"
            )
            
            logger.info(
                "Author papers retrieved",
                author_id=author_id,
                paper_count=len(result.get("papers", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get author papers failed", error=str(e))
            raise
    
    async def get_author_coauthors(self, author_id: str) -> Dict[str, Any]:
        """获取作者合作者 - GET /authors/:id/coauthors"""
        logger.info("Getting author coauthors", author_id=author_id)
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint=f"/authors/{author_id}/coauthors"
            )
            
            logger.info(
                "Author coauthors retrieved",
                author_id=author_id,
                coauthor_count=len(result.get("coauthors", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get author coauthors failed", error=str(e))
            raise

    # ============ 网络分析接口 ============
    
    async def get_citation_network(
        self,
        seed_papers: List[str],
        depth: int = 2,
        direction: str = "both",
        max_nodes: int = 50
    ) -> Dict[str, Any]:
        """获取引用网络 - 基于论文引用关系构建"""
        logger.info(
            "Getting citation network via Go service",
            seed_papers=seed_papers,
            depth=depth,
            max_nodes=max_nodes
        )
        
        try:
            # 使用第一个种子论文获取网络
            if not seed_papers:
                return {"nodes": [], "edges": []}
            
            paper_id = seed_papers[0]
            result = await self._make_request(
                method="GET",
                endpoint=f"/network/paper/{paper_id}",
                params={"depth": depth, "max_nodes": max_nodes}
            )
            
            # 转换为标准格式
            graph_data = result.get("graph", {})
            
            logger.info(
                "Citation network retrieved",
                node_count=len(graph_data.get("nodes", [])),
                edge_count=len(graph_data.get("edges", []))
            )
            
            return graph_data
            
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            raise
    
    async def get_collaboration_network(
        self,
        authors: List[str],
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取合作网络 - GET /network/author/:id"""
        logger.info(
            "Getting collaboration network via Go service",
            authors=authors,
            time_range=time_range
        )
        
        try:
            # 使用第一个作者获取网络
            if not authors:
                return {"nodes": [], "edges": []}
            
            author_id = authors[0]
            result = await self._make_request(
                method="GET",
                endpoint=f"/network/author/{author_id}",
                params={"depth": 1, "max_nodes": 50}
            )
            
            # 转换为标准格式
            graph_data = result.get("graph", {})
            
            logger.info(
                "Collaboration network retrieved",
                node_count=len(graph_data.get("nodes", [])),
                edge_count=len(graph_data.get("edges", []))
            )
            
            return graph_data
            
        except Exception as e:
            logger.error("Get collaboration network failed", error=str(e))
            raise

    # ============ 趋势分析接口 ============
    
    async def get_research_trends(
        self,
        domain: str,
        time_range: str,
        metrics: List[str],
        granularity: str = "year"
    ) -> Dict[str, Any]:
        """获取研究趋势 - 基于热门论文和关键词分析"""
        logger.info(
            "Getting research trends via Go service",
            domain=domain,
            time_range=time_range,
            metrics=metrics,
            granularity=granularity
        )
        
        try:
            # 解析时间范围
            years = time_range.split("-")
            start_year = int(years[0]) if len(years) > 0 else 2020
            end_year = int(years[1]) if len(years) > 1 else 2024
            
            # 获取不同时间窗口的热门论文来分析趋势
            trend_data = []
            
            for year in range(start_year, end_year + 1):
                # 搜索该年份该领域的论文
                papers_result = await self.search_papers(
                    query=domain,
                    filters={"year": year},
                    limit=100
                )
                
                paper_count = len(papers_result.get("papers", []))
                citation_count = sum(
                    paper.get("citations", 0) 
                    for paper in papers_result.get("papers", [])
                )
                
                trend_data.append({
                    "time_period": str(year),
                    "value": paper_count if "publication_count" in metrics else citation_count,
                    "label": f"{year}年"
                })
            
            result = {
                "domain": domain,
                "time_range": time_range,
                "data_points": trend_data,
                "metrics": metrics
            }
            
            logger.info(
                "Research trends retrieved",
                data_points=len(trend_data)
            )
            
            return result
            
        except Exception as e:
            logger.error("Get research trends failed", error=str(e))
            raise
    
    async def analyze_research_landscape(
        self,
        domain: str,
        analysis_dimensions: List[str]
    ) -> Dict[str, Any]:
        """分析研究领域全景 - 综合多个接口数据"""
        logger.info(
            "Analyzing research landscape via Go service",
            domain=domain,
            dimensions=analysis_dimensions
        )
        
        try:
            landscape_data = {}
            
            # 获取热门话题
            if "topics" in analysis_dimensions:
                keywords_result = await self.get_top_keywords()
                # 过滤与领域相关的关键词
                relevant_keywords = [
                    kw for kw in keywords_result.get("keywords", [])
                    if domain.lower() in kw.get("keyword", "").lower()
                ]
                landscape_data["hot_topics"] = [
                    {
                        "name": kw["keyword"],
                        "paper_count": kw["paper_count"],
                        "score": kw["paper_count"] / 100.0
                    }
                    for kw in relevant_keywords[:10]
                ]
            
            # 获取热门论文和作者
            if "authors" in analysis_dimensions:
                papers_result = await self.search_papers(
                    query=domain,
                    limit=50
                )
                
                # 统计活跃作者
                author_stats = {}
                for paper in papers_result.get("papers", []):
                    for author in paper.get("authors", []):
                        author_name = author.get("name", "")
                        if author_name:
                            if author_name not in author_stats:
                                author_stats[author_name] = {
                                    "name": author_name,
                                    "paper_count": 0,
                                    "affiliation": author.get("affiliation", "")
                                }
                            author_stats[author_name]["paper_count"] += 1
                
                # 排序并取前10
                top_authors = sorted(
                    author_stats.values(),
                    key=lambda x: x["paper_count"],
                    reverse=True
                )[:10]
                
                landscape_data["active_authors"] = top_authors
            
            # 获取热门论文作为新兴趋势
            if "trends" in analysis_dimensions:
                trending_result = await self.get_trending_papers(
                    time_window="month",
                    limit=10
                )
                
                landscape_data["emerging_trends"] = [
                    {
                        "name": paper.get("title", "")[:50] + "...",
                        "growth_rate": paper.get("popularity_score", 0) * 10,
                        "description": f"热门论文，引用数: {paper.get('citations', 0)}"
                    }
                    for paper in trending_result.get("trending_papers", [])[:5]
                ]
            
            logger.info("Research landscape analysis completed")
            
            return landscape_data
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            raise
    
    # ============ 辅助接口 ============
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 使用简单的论文搜索作为健康检查
            result = await self.search_papers(
                query="test",
                limit=1
            )
            
            logger.debug("Go service health check passed")
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error("Go service health check failed", error=str(e))
            raise
    
    async def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        try:
            # 获取热门关键词作为服务信息的一部分
            keywords_result = await self.get_top_keywords()
            
            result = {
                "service": "OpenResearch Go Service",
                "version": "1.0.0",
                "base_url": self.base_url,
                "available_endpoints": [
                    "/papers",
                    "/authors", 
                    "/network/paper/:id",
                    "/network/author/:id",
                    "/papers/trending",
                    "/papers/keywords/top"
                ],
                "total_keywords": len(keywords_result.get("keywords", []))
            }
            
            logger.debug("Go service info retrieved", info=result)
            return result
            
        except Exception as e:
            logger.error("Get service info failed", error=str(e))
            raise

# 创建全局客户端实例
go_client = GoServiceClient()

