from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class PaperType(str, Enum):
    """Paper Type"""
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    WORKSHOP = "workshop"
    THESIS = "thesis"

class Author(BaseModel):
    """Author Information Model - MVP Version"""
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
    """Paper Information Model - MVP Version"""
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
    
    # Basic Information
    keywords: List[str] = []
    language: str = "en"
    
    # Basic Metrics
    citation_count: Optional[int] = None
    download_count: Optional[int] = None

class SearchMetadata(BaseModel):
    """Search Metadata - MVP Version"""
    total_count: int
    page: int = 1
    page_size: int = 20
    execution_time_ms: int
    query: str
    filters_applied: Dict[str, Any] = {}

class SearchResult(BaseModel):
    """Search Result Model - MVP Version"""
    papers: List[Paper]
    metadata: SearchMetadata

class NetworkNode(BaseModel):
    """Network Node - MVP Version"""
    id: str
    label: str
    type: str  # paper, author, institution
    properties: Dict[str, Any] = {}

class NetworkEdge(BaseModel):
    """Network Edge - MVP Version"""
    source: str
    target: str
    weight: Optional[float] = 1.0
    edge_type: str  # citation, collaboration

class NetworkAnalysis(BaseModel):
    """Network Analysis Result - MVP Version"""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    node_count: int
    edge_count: int

class TrendData(BaseModel):
    """Trend Data Point"""
    time_period: str
    value: float
    label: Optional[str] = None

class TrendAnalysis(BaseModel):
    """Trend Analysis Result - MVP Version"""
    domain: str
    time_range: str
    data_points: List[TrendData]
    metrics: List[str]