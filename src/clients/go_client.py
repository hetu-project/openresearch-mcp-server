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
    """Go Service Client - Based on actual API documentation"""
    
    def __init__(self):
        self.base_url = settings.go_service_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=settings.go_service_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Thread-safe simplified connection"""
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
        """Disconnect"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Go service client disconnected")
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure session exists and return non-None session"""
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
        """Send HTTP request"""
        session = await self._ensure_session()
        
        url = f"{self.base_url}{endpoint}"
        logger.info("tools_params params", tools_params=params)
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

    # ============ Paper Related APIs ============
    
    async def search_papers(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "relevance",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search papers - GET /papers"""
        logger.info(
            "Searching papers via Go service",
            query=query,
            filters=filters,
            limit=limit
        )
        
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
    
    async def get_paper_details(self, titles: List[str],limit: int = 2) -> Dict[str, Any]:
        """Get paper details - Search by titles"""
        logger.info("Getting paper details via titles", titles=titles)
        
        try:
            all_papers = []
            
            for title in titles:
                result = await self._make_request(
                    method="GET",
                    endpoint="/papers",
                    params={"title": title, "limit": limit}
                )
                
                papers = result.get("papers", [])
                if papers:
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
        """Get paper citations - GET /papers/:id/citations"""
        logger.info("Getting paper citations", paper_id=paper_id)
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint=f"/papers/{paper_id}/citations"
            )
            
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
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
        """Get paper recommendations - GET /papers/:id/recommendations"""
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
        """Get trending papers - GET /papers/trending"""
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
            
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            result.setdefault('trending_papers', [])
            result.setdefault('count', len(result.get('trending_papers', [])))
            result.setdefault('time_window', time_window)
            
            papers = result.get('trending_papers', [])
            for paper in papers:
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
        """Get top keywords - GET /papers/keywords/top"""
        logger.info("Getting top keywords")
        
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/papers/keywords/top"
            )
            
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            result.setdefault('keywords', [])
            result.setdefault('count', len(result.get('keywords', [])))
            
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

    # ============ Author Related APIs ============
    
    async def search_authors(
        self,
        query: Optional[str] = None,
        author_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search authors - Support search by name, ID or other conditions - GET /authors"""
        logger.info(
            "Searching authors via Go service",
            query=query,
            author_id=author_id,
            filters=filters,
            limit=limit
        )
        
        params = {}
        
        if author_id:
            params["id"] = author_id
        elif query:
            params["name"] = query
        
        if filters:
            if filters.get("affiliation"):
                params["affiliation"] = filters["affiliation"]
            if filters.get("research_area"):
                params["interest"] = filters["research_area"]
        
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
        """Get author's published papers - GET /authors/:id/papers"""
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
        """Get author's collaborators - GET /authors/:id/coauthors"""
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

    # ============ Network Analysis APIs ============
    
    async def get_citation_network(
        self,
        seed_papers: List[str],
        depth: int = 2,
        direction: str = "both",
        max_nodes: int = 50
    ) -> Dict[str, Any]:
        """Get citation network - build based on paper citation relationships"""
        logger.info(
            "Getting citation network via Go service",
            seed_papers=seed_papers,
            depth=depth,
            max_nodes=max_nodes
        )
        
        try:
            if not seed_papers:
                return {"nodes": [], "edges": []}
            
            paper_id = seed_papers[0]
            result = await self._make_request(
                method="GET",
                endpoint=f"/network/paper/{paper_id}",
                params={"depth": depth, "max_nodes": max_nodes}
            )
            
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
        """Get collaboration network - GET /network/author/:id"""
        logger.info(
            "Getting collaboration network via Go service",
            authors=authors,
            time_range=time_range
        )
        
        try:
            if not authors:
                return {"nodes": [], "edges": []}
            
            author_id = authors[0]
            result = await self._make_request(
                method="GET",
                endpoint=f"/network/author/{author_id}",
                params={"depth": 1, "max_nodes": 50}
            )
            
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

    async def get_research_trends(
        self,
        domain: str,
        time_range: str,
        metrics: List[str],
        granularity: str = "year"
    ) -> Dict[str, Any]:
        """Get research trends - based on popular papers and keyword analysis"""
        logger.info(
            "Getting research trends via Go service",
            domain=domain,
            time_range=time_range,
            metrics=metrics,
            granularity=granularity
        )
        
        try:
            years = time_range.split("-")
            start_year = int(years[0]) if len(years) > 0 else 2020
            end_year = int(years[1]) if len(years) > 1 else 2024
            
            trend_data = []
            
            for year in range(start_year, end_year + 1):
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
                    "label": f"Year {year}"
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
        """Analyze research field landscape - integrate multiple interface data"""
        logger.info(
            "Analyzing research landscape via Go service",
            domain=domain,
            dimensions=analysis_dimensions
        )
        
        try:
            landscape_data = {}
            
            if "topics" in analysis_dimensions:
                keywords_result = await self.get_top_keywords()
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
            
            if "authors" in analysis_dimensions:
                papers_result = await self.search_papers(
                    query=domain,
                    limit=50
                )
                
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
                
                top_authors = sorted(
                    author_stats.values(),
                    key=lambda x: x["paper_count"],
                    reverse=True
                )[:10]
                
                landscape_data["active_authors"] = top_authors
            
            if "trends" in analysis_dimensions:
                trending_result = await self.get_trending_papers(
                    time_window="month",
                    limit=10
                )
                
                landscape_data["emerging_trends"] = [
                    {
                        "name": paper.get("title", "")[:50] + "...",
                        "growth_rate": paper.get("popularity_score", 0) * 10,
                        "description": f"Popular paper, citations: {paper.get('citations', 0)}"
                    }
                    for paper in trending_result.get("trending_papers", [])[:5]
                ]
            
            logger.info("Research landscape analysis completed")
            
            return landscape_data
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        try:
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
        """Get service information"""
        try:
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

go_client = GoServiceClient()