# src/models/data_models.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class PaperType(str, Enum):
    """论文类型"""
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    WORKSHOP = "workshop"
    THESIS = "thesis"

class Author(BaseModel):
    """作者信息模型 - MVP版本"""
    id: str
    name: str
    email: Optional[str] = None
    orcid: Optional[str] = None
    affiliations: List[str] = []
    h_index: Optional[int] = None
    citation_count: Optional[int] = None
    paper_count: Optional[int] = None
    research_interests: List[str] = []

class Paper(BaseModel):
    """论文信息模型 - MVP版本"""
    id: str
    title: str
    abstract: Optional[str] = None
    authors: List[Author] = []
    publication_date: Optional[datetime] = None
    venue: Optional[str] = None
    venue_type: Optional[PaperType] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    
    # 基础信息
    keywords: List[str] = []
    language: str = "en"
    
    # 基础指标
    citation_count: Optional[int] = None
    download_count: Optional[int] = None

class SearchMetadata(BaseModel):
    """搜索元数据 - MVP版本"""
    total_count: int
    page: int = 1
    page_size: int = 20
    execution_time_ms: int
    query: str
    filters_applied: Dict[str, Any] = {}

class SearchResult(BaseModel):
    """搜索结果模型 - MVP版本"""
    papers: List[Paper]
    metadata: SearchMetadata

class NetworkNode(BaseModel):
    """网络节点 - MVP版本"""
    id: str
    label: str
    type: str  # paper, author, institution
    properties: Dict[str, Any] = {}

class NetworkEdge(BaseModel):
    """网络边 - MVP版本"""
    source: str
    target: str
    weight: Optional[float] = 1.0
    edge_type: str  # citation, collaboration

class NetworkAnalysis(BaseModel):
    """网络分析结果 - MVP版本"""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    node_count: int
    edge_count: int

class TrendData(BaseModel):
    """趋势数据点"""
    time_period: str
    value: float
    label: Optional[str] = None

class TrendAnalysis(BaseModel):
    """趋势分析结果 - MVP版本"""
    domain: str
    time_range: str
    data_points: List[TrendData]
    metrics: List[str]