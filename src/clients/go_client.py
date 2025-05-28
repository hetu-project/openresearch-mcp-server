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
    """Go服务客户端 - MVP版本"""
    
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
        # 快速检查，避免不必要的锁竞争
        if self.session and not self.session.closed:
            return
            
        async with self._session_lock:
            # 双重检查模式 - 这就足够了！
            if self.session and not self.session.closed:
                return
            
            old_session = self.session
            new_session = None    
            connector = None

            # 创建新连接
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

                # 清理旧连接
                if old_session and not old_session.closed:
                    try:
                        asyncio.create_task(old_session.close())
                    except Exception as e:
                        logger.warning("Failed to close old session", error=str(e))

                logger.info("Go service client connected", base_url=self.base_url)
                
            except Exception as e:
                # 创建失败时清理资源
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
                
                # 检查响应状态
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
                
                # 解析响应
                try:
                    result = await response.json()
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
    
    async def search_papers(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "relevance",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """搜索论文"""
        logger.info(
            "Searching papers via Go service",
            query=query,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
        request_data = {
            "query": query,
            "filters": filters or {},
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/papers/search",
                data=request_data
            )
            
            logger.info(
                "Paper search completed",
                total_count=result.get("total_count", 0),
                returned_count=len(result.get("papers", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Paper search failed", error=str(e))
            raise
    
    async def get_paper_details(self, paper_ids: List[str]) -> Dict[str, Any]:
        """获取论文详情"""
        logger.info("Getting paper details via Go service", paper_ids=paper_ids)
        
        request_data = {
            "paper_ids": paper_ids
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/papers/details",
                data=request_data
            )
            
            logger.info(
                "Paper details retrieved",
                requested_count=len(paper_ids),
                returned_count=len(result.get("papers", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get paper details failed", error=str(e))
            raise
    
    async def search_authors(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """搜索作者"""
        logger.info(
            "Searching authors via Go service",
            query=query,
            filters=filters,
            limit=limit
        )
        
        request_data = {
            "query": query,
            "filters": filters or {},
            "limit": limit
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/authors/search",
                data=request_data
            )
            
            logger.info(
                "Author search completed",
                returned_count=len(result.get("authors", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Author search failed", error=str(e))
            raise
    
    async def get_author_details(self, author_ids: List[str]) -> Dict[str, Any]:
        """获取作者详情"""
        logger.info("Getting author details via Go service", author_ids=author_ids)
        
        request_data = {
            "author_ids": author_ids
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/authors/details",
                data=request_data
            )
            
            logger.info(
                "Author details retrieved",
                requested_count=len(author_ids),
                returned_count=len(result.get("authors", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get author details failed", error=str(e))
            raise
    
    async def get_citation_network(
        self,
        seed_papers: List[str],
        depth: int = 2,
        direction: str = "both",
        max_nodes: int = 50
    ) -> Dict[str, Any]:
        """获取引用网络"""
        logger.info(
            "Getting citation network via Go service",
            seed_papers=seed_papers,
            depth=depth,
            direction=direction,
            max_nodes=max_nodes
        )
        
        request_data = {
            "seed_papers": seed_papers,
            "depth": depth,
            "direction": direction,
            "max_nodes": max_nodes
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/networks/citation",
                data=request_data
            )
            
            logger.info(
                "Citation network retrieved",
                node_count=len(result.get("nodes", [])),
                edge_count=len(result.get("edges", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            raise
    
    async def get_collaboration_network(
        self,
        authors: List[str],
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取合作网络"""
        logger.info(
            "Getting collaboration network via Go service",
            authors=authors,
            time_range=time_range
        )
        
        request_data = {
            "authors": authors,
            "time_range": time_range
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/networks/collaboration",
                data=request_data
            )
            
            logger.info(
                "Collaboration network retrieved",
                node_count=len(result.get("nodes", [])),
                edge_count=len(result.get("edges", []))
            )
            
            return result
            
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
        """获取研究趋势"""
        logger.info(
            "Getting research trends via Go service",
            domain=domain,
            time_range=time_range,
            metrics=metrics,
            granularity=granularity
        )
        
        request_data = {
            "domain": domain,
            "time_range": time_range,
            "metrics": metrics,
            "granularity": granularity
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/trends/research",
                data=request_data
            )
            
            logger.info(
                "Research trends retrieved",
                data_points=len(result.get("data_points", []))
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
        """分析研究领域全景"""
        logger.info(
            "Analyzing research landscape via Go service",
            domain=domain,
            dimensions=analysis_dimensions
        )
        
        request_data = {
            "domain": domain,
            "analysis_dimensions": analysis_dimensions
        }
        
        try:
            result = await self._make_request(
                method="POST",
                endpoint="/api/v1/analysis/landscape",
                data=request_data
            )
            
            logger.info("Research landscape analysis completed")
            
            return result
            
        except Exception as e:
            logger.error("Analyze research landscape failed", error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/health"
            )
            
            logger.debug("Go service health check passed")
            return result
            
        except Exception as e:
            logger.error("Go service health check failed", error=str(e))
            raise
    
    async def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        try:
            result = await self._make_request(
                method="GET",
                endpoint="/api/v1/info"
            )
            
            logger.debug("Go service info retrieved", info=result)
            return result
            
        except Exception as e:
            logger.error("Get service info failed", error=str(e))
            raise

# 创建全局客户端实例
go_client = GoServiceClient()
