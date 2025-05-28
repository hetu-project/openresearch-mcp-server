# src/models/tool_schemas.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .data_models import SearchResult, Paper, Author

# 输入模型
class SearchPapersInput(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
    sort_by: str = "relevance"
    limit: int = 20
    offset: int = 0

class GetPaperDetailsInput(BaseModel):
    paper_ids: List[str]
    include_citations: bool = False

class SearchAuthorsInput(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: int = 20

class GetAuthorDetailsInput(BaseModel):
    author_ids: List[str]

# 输出模型
class BaseOutput(BaseModel):
    success: bool
    execution_time_ms: int
    error: Optional[str] = None

class SearchPapersOutput(BaseOutput):
    data: Optional[SearchResult] = None

class GetPaperDetailsOutput(BaseOutput):
    data: Optional[List[Paper]] = None

class SearchAuthorsOutput(BaseOutput):
    data: Optional[List[Author]] = None

class GetAuthorDetailsOutput(BaseOutput):
    data: Optional[List[Author]] = None
