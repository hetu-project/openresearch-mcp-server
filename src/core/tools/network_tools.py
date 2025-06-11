from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class NetworkTools(BaseTools):
    """Network Analysis Tools - Support JSON format"""
    
    def get_tools(self) -> List[Tool]:
        """Get tool definitions"""
        return [
            Tool(
                name="get_citation_network",
                description="Get paper citation network, analyze citation relationships between papers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "seed_papers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of seed paper IDs"
                        },
                        "depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                            "default": 2,
                            "description": "Network depth"
                        },
                        "direction": {
                            "type": "string",
                            "enum": ["incoming", "outgoing", "both"],
                            "default": "both",
                            "description": "Citation direction: incoming(cited), outgoing(citing), both(bidirectional)"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 200,
                            "default": 50,
                            "description": "Maximum number of nodes"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown(formatted display) or json(raw data)"
                        }
                    },
                    "required": ["seed_papers"]
                }
            ),
            Tool(
                name="get_collaboration_network",
                description="Get author collaboration network, analyze collaboration relationships between authors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "authors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of author IDs"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range, format: YYYY-YYYY"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 200,
                            "default": 50,
                            "description": "Maximum number of nodes"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "Return format: markdown(formatted display) or json(raw data)"
                        }
                    },
                    "required": ["authors"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_citation_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get citation network tool - Support JSON format"""
        seed_papers = arguments["seed_papers"]
        depth = arguments.get("depth", 2)
        direction = arguments.get("direction", "both")
        max_nodes = arguments.get("max_nodes", 50)
        return_format = arguments.get("format", "json")

        logger.info(
            "Getting citation network", 
            seed_papers=seed_papers, 
            depth=depth, 
            direction=direction,
            max_nodes=max_nodes,
            format=return_format
        )
        
        try:
            raw_result = await self.go_client.get_citation_network(
                seed_papers=seed_papers,
                depth=depth,
                direction=direction,
                max_nodes=max_nodes
            )
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_citation_network(raw_result, seed_papers)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get Citation Network")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_collaboration_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get collaboration network tool - Support JSON format"""
        authors = arguments["authors"]
        time_range = arguments.get("time_range")
        max_nodes = arguments.get("max_nodes", 50)
        return_format = arguments.get("format", "json")
        
        logger.info(
            "Getting collaboration network", 
            authors=authors, 
            time_range=time_range,
            max_nodes=max_nodes,
            format=return_format
        )
        
        try:
            raw_result = await self.go_client.get_collaboration_network(
                authors=authors,
                time_range=time_range
            )
            
            if return_format == "json":
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                content = self._format_collaboration_network(raw_result, authors)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get collaboration network failed", error=str(e))
            error_content = self._format_error_response(str(e), "Get Collaboration Network")
            return [TextContent(type="text", text=error_content)]
    
    def _format_citation_network(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """Format citation network results"""
        nodes = raw_result.get("nodes", [])
        edges = raw_result.get("edges", [])
        
        content = f"# Citation Network Analysis\n\n"
        content += f"**Seed Paper ID**: {paper_id}\n"
        content += f"**Network Size**: {len(nodes)} nodes, {len(edges)} edges\n\n"
        
        if not nodes:
            content += "No relevant citation network found.\n"
            return content
        
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        content += "## Network Composition\n"
        for node_type, count in node_types.items():
            content += f"- {node_type}: {count}\n"
        content += "\n"
        
        paper_nodes = [node for node in nodes if node.get("type") == "paper"]
        if paper_nodes:
            content += "## Important Paper Nodes\n"
            
            paper_nodes.sort(
                key=lambda x: x.get("properties", {}).get("citations", 0),
                reverse=True
            )
            
            for i, node in enumerate(paper_nodes[:10], 1):
                label = self._safe_get_str(node, "label", "Unknown Paper")
                properties = node.get("properties", {})
                citations = self._safe_get_int(properties, "citations")
                
                content += f"{i}. **{self._truncate_text(label, 80)}**"
                if citations > 0:
                    content += f" (Citations: {citations})"
                content += "\n"
        
        edge_types = {}
        for edge in edges:
            edge_type = edge.get("type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        if edge_types:
            content += "\n## Relationship Types\n"
            for edge_type, count in edge_types.items():
                content += f"- {edge_type}: {count}\n"
        
        content += f"\n## Network Statistics\n"
        if len(nodes) > 0:
            avg_degree = (len(edges) * 2) / len(nodes)
            content += f"- Average Degree: {avg_degree:.2f}\n"
        content += f"- Network Density: {len(edges) / max(1, len(nodes) * (len(nodes) - 1) / 2):.4f}\n"
        
        return content
    
    def _format_collaboration_network(self, raw_result: Dict[str, Any], author_id: str) -> str:
        """Format collaboration network results"""
        nodes = raw_result.get("nodes", [])
        edges = raw_result.get("edges", [])
        
        content = f"# Collaboration Network Analysis\n\n"
        content += f"**Core Author ID**: {author_id}\n"
        content += f"**Network Size**: {len(nodes)} nodes, {len(edges)} edges\n\n"
        
        if not nodes:
            content += "No relevant collaboration network found.\n"
            return content
        
        author_nodes = [node for node in nodes if node.get("type") == "author"]
        
        if author_nodes:
            content += f"## Authors in Network ({len(author_nodes)})\n"
            
            for i, node in enumerate(author_nodes[:20], 1):
                label = self._safe_get_str(node, "label", "Unknown Author")
                properties = node.get("properties", {})
                affiliation = self._safe_get_str(properties, "affiliation")
                paper_count = self._safe_get_int(properties, "paper_count")
                citation_count = self._safe_get_int(properties, "citation_count")
                
                content += f"{i}. **{label}**"
                if affiliation:
                    content += f" ({affiliation})"
                if paper_count > 0:
                    content += f" - {paper_count} papers"
                if citation_count > 0:
                    content += f", {citation_count} citations"
                content += "\n"
        
        collaboration_edges = [edge for edge in edges if edge.get("type") == "collaborates"]
        
        content += f"\n## Collaboration Statistics\n"
        content += f"- Number of Collaborations: {len(collaboration_edges)}\n"
        
        if len(author_nodes) > 0:
            avg_collaborators = len(collaboration_edges) * 2 / len(author_nodes)
            content += f"- Average Number of Collaborators: {avg_collaborators:.2f}\n"
        
        if collaboration_edges:
            content += f"\n## Main Collaborations\n"
            
            collaboration_edges.sort(
                key=lambda x: x.get("properties", {}).get("papers_count", 0),
                reverse=True
            )
            
            for i, edge in enumerate(collaboration_edges[:10], 1):
                source_id = edge.get("source", "")
                target_id = edge.get("target", "")
                properties = edge.get("properties", {})
                papers_count = self._safe_get_int(properties, "papers_count")
                
                source_name = "Unknown"
                target_name = "Unknown"
                
                for node in author_nodes:
                    if node.get("id") == source_id:
                        source_name = self._safe_get_str(node, "label", "Unknown")
                    elif node.get("id") == target_id:
                        target_name = self._safe_get_str(node, "label", "Unknown")
                
                content += f"{i}. **{source_name}** ↔ **{target_name}**"
                if papers_count > 0:
                    content += f" (Collaborative Papers: {papers_count})"
                content += "\n"
        
        return content