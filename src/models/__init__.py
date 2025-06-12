"""
Data Models Module - MVP Version

This module contains all data models and schemas for the OpenResearch MCP server.
Includes core data models, tool input/output schemas, and utility functions.
"""

# Core data models
from .data_models import (
    PaperType,
    Author,
    Paper,
    SearchMetadata,
    SearchResult,
    NetworkNode,
    NetworkEdge,
    NetworkAnalysis,
    TrendData,
    TrendAnalysis
)

# Tool schemas
from .tool_schemas import (
    # Input schemas
    SearchPapersInput,
    GetPaperDetailsInput,
    SearchAuthorsInput,
    GetAuthorDetailsInput,
    
    # Output schemas
    BaseOutput,
    SearchPapersOutput,
    GetPaperDetailsOutput,
    SearchAuthorsOutput,
    GetAuthorDetailsOutput
)

# Export all models and schemas
__all__ = [
    # Core data models
    "PaperType",
    "Author",
    "Paper", 
    "SearchMetadata",
    "SearchResult",
    "NetworkNode",
    "NetworkEdge",
    "NetworkAnalysis",
    "TrendData",
    "TrendAnalysis",
    
    # Tool input schemas
    "SearchPapersInput",
    "GetPaperDetailsInput", 
    "SearchAuthorsInput",
    "GetAuthorDetailsInput",
    
    # Tool output schemas
    "BaseOutput",
    "SearchPapersOutput",
    "GetPaperDetailsOutput",
    "SearchAuthorsOutput",
    "GetAuthorDetailsOutput",
    
    # Utility functions
    "get_all_models",
    "get_input_schemas",
    "get_output_schemas",
    "validate_model"
]

def get_all_models():
    """
    Get all available data models.
    
    Returns:
        dict: Dictionary mapping model names to model classes
    """
    return {
        # Core models
        "Author": Author,
        "Paper": Paper,
        "SearchMetadata": SearchMetadata,
        "SearchResult": SearchResult,
        "NetworkNode": NetworkNode,
        "NetworkEdge": NetworkEdge,
        "NetworkAnalysis": NetworkAnalysis,
        "TrendData": TrendData,
        "TrendAnalysis": TrendAnalysis,
    }

def get_input_schemas():
    """
    Get all tool input schemas.
    
    Returns:
        dict: Dictionary mapping schema names to schema classes
    """
    return {
        "SearchPapersInput": SearchPapersInput,
        "GetPaperDetailsInput": GetPaperDetailsInput,
        "SearchAuthorsInput": SearchAuthorsInput,
        "GetAuthorDetailsInput": GetAuthorDetailsInput,
    }

def get_output_schemas():
    """
    Get all tool output schemas.
    
    Returns:
        dict: Dictionary mapping schema names to schema classes
    """
    return {
        "BaseOutput": BaseOutput,
        "SearchPapersOutput": SearchPapersOutput,
        "GetPaperDetailsOutput": GetPaperDetailsOutput,
        "SearchAuthorsOutput": SearchAuthorsOutput,
        "GetAuthorDetailsOutput": GetAuthorDetailsOutput,
    }

def validate_model(model_class, data):
    """
    Validate data against a model schema.
    
    Args:
        model_class: Pydantic model class
        data: Data to validate
        
    Returns:
        tuple: (is_valid: bool, result: model_instance or error_message)
    """
    try:
        if isinstance(data, dict):
            validated = model_class(**data)
        else:
            validated = model_class(data)
        return True, validated
    except Exception as e:
        return False, str(e)

# Model categories for organization
MODEL_CATEGORIES = {
    "core": {
        "name": "Core Data Models",
        "description": "Basic data structures for academic research",
        "models": ["Author", "Paper", "SearchResult", "SearchMetadata"]
    },
    "network": {
        "name": "Network Analysis Models", 
        "description": "Models for network analysis and visualization",
        "models": ["NetworkNode", "NetworkEdge", "NetworkAnalysis"]
    },
    "trend": {
        "name": "Trend Analysis Models",
        "description": "Models for trend analysis and research landscape",
        "models": ["TrendData", "TrendAnalysis"]
    },
    "schemas": {
        "name": "Tool Schemas",
        "description": "Input/output schemas for tool validation",
        "models": [
            "SearchPapersInput", "SearchPapersOutput",
            "GetPaperDetailsInput", "GetPaperDetailsOutput", 
            "SearchAuthorsInput", "SearchAuthorsOutput",
            "GetAuthorDetailsInput", "GetAuthorDetailsOutput"
        ]
    }
}

def get_model_categories():
    """
    Get information about model categories.
    
    Returns:
        dict: Model categories with descriptions
    """
    return MODEL_CATEGORIES

def get_models_by_category(category: str):
    """
    Get models for a specific category.
    
    Args:
        category: Category name ("core", "network", "trend", "schemas")
        
    Returns:
        list: List of model names in the category
    """
    return MODEL_CATEGORIES.get(category, {}).get("models", [])

# Common field types and validators
COMMON_FIELD_TYPES = {
    "id": str,
    "name": str,
    "email": str,
    "url": str,
    "doi": str,
    "count": int,
    "score": float,
    "date": "datetime",
    "list_str": "List[str]",
    "optional_str": "Optional[str]",
    "optional_int": "Optional[int]"
}

def get_common_field_types():
    """
    Get common field types used across models.
    
    Returns:
        dict: Dictionary of common field types
    """
    return COMMON_FIELD_TYPES

# Model validation helpers
def create_empty_search_result():
    """Create an empty search result for error cases."""
    return SearchResult(
        papers=[],
        metadata=SearchMetadata(
            total_count=0,
            execution_time_ms=0,
            query=""
        )
    )

def create_error_output(error_message: str, execution_time_ms: int = 0):
    """Create a standardized error output."""
    return BaseOutput(
        success=False,
        error=error_message,
        execution_time_ms=execution_time_ms
    )

def create_success_output(execution_time_ms: int = 0):
    """Create a standardized success output."""
    return BaseOutput(
        success=True,
        execution_time_ms=execution_time_ms
    )
