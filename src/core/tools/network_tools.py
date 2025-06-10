# src/core/tools/network_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
import json
from .base_tools import BaseTools
from src.utils.error_handler import handle_tool_error

logger = structlog.get_logger()

class NetworkTools(BaseTools):
    """网络分析工具 - 支持JSON格式返回"""
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="get_citation_network",
                description="获取论文引用网络，分析论文之间的引用关系",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "seed_papers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "种子论文ID列表"
                        },
                        "depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                            "default": 2,
                            "description": "网络深度"
                        },
                        "direction": {
                            "type": "string",
                            "enum": ["incoming", "outgoing", "both"],
                            "default": "both",
                            "description": "引用方向：incoming(被引用), outgoing(引用), both(双向)"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 200,
                            "default": 50,
                            "description": "最大节点数"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["seed_papers"]
                }
            ),
            Tool(
                name="get_collaboration_network",
                description="获取作者合作网络，分析作者之间的合作关系",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "authors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "作者ID列表"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，格式：YYYY-YYYY"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 200,
                            "default": 50,
                            "description": "最大节点数"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "default": "markdown",
                            "description": "返回格式：markdown(格式化显示) 或 json(原始数据)"
                        }
                    },
                    "required": ["authors"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_citation_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取引用网络工具 - 支持JSON格式"""
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
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_citation_network(raw_result, seed_papers)
                return [TextContent(type="text", text=content)]
              
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取引用网络")
            return [TextContent(type="text", text=error_content)]
    
    @handle_tool_error
    async def get_collaboration_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取合作网络工具 - 支持JSON格式"""
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
                # 返回原始 JSON
                return [TextContent(type="text", text=json.dumps(raw_result, ensure_ascii=False, indent=2))]
            else:
                # 返回格式化的 Markdown（默认）
                content = self._format_collaboration_network(raw_result, authors)
                return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get collaboration network failed", error=str(e))
            error_content = self._format_error_response(str(e), "获取合作网络")
            return [TextContent(type="text", text=error_content)]
    
    def _format_citation_network(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """格式化引用网络结果"""
        nodes = raw_result.get("nodes", [])
        edges = raw_result.get("edges", [])
        
        content = f"# 引用网络分析\n\n"
        content += f"**种子论文ID**: {paper_id}\n"
        content += f"**网络规模**: {len(nodes)} 个节点, {len(edges)} 条边\n\n"
        
        if not nodes:
            content += "未找到相关的引用网络。\n"
            return content
        
        # 统计节点类型
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        content += "## 网络组成\n"
        for node_type, count in node_types.items():
            content += f"- {node_type}: {count} 个\n"
        content += "\n"
        
        # 显示重要节点（论文）
        paper_nodes = [node for node in nodes if node.get("type") == "paper"]
        if paper_nodes:
            content += "## 重要论文节点\n"
            
            # 按引用数排序（如果有的话）
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
                    content += f" (引用数: {citations})"
                content += "\n"
        
        # 边类型统计
        edge_types = {}
        for edge in edges:
            edge_type = edge.get("type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        if edge_types:
            content += "\n## 关系类型\n"
            for edge_type, count in edge_types.items():
                content += f"- {edge_type}: {count} 条\n"
        
        # 网络统计
        content += f"\n## 网络统计\n"
        if len(nodes) > 0:
            avg_degree = (len(edges) * 2) / len(nodes)
            content += f"- 平均度数: {avg_degree:.2f}\n"
        content += f"- 网络密度: {len(edges) / max(1, len(nodes) * (len(nodes) - 1) / 2):.4f}\n"
        
        return content
    
    def _format_collaboration_network(self, raw_result: Dict[str, Any], author_id: str) -> str:
        """格式化合作网络结果"""
        nodes = raw_result.get("nodes", [])
        edges = raw_result.get("edges", [])
        
        content = f"# 合作网络分析\n\n"
        content += f"**核心作者ID**: {author_id}\n"
        content += f"**网络规模**: {len(nodes)} 个节点, {len(edges)} 条边\n\n"
        
        if not nodes:
            content += "未找到相关的合作网络。\n"
            return content
        
        # 显示作者节点
        author_nodes = [node for node in nodes if node.get("type") == "author"]
        
        if author_nodes:
            content += f"## 网络中的作者 ({len(author_nodes)} 位)\n"
            
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
                    content += f" - {paper_count} 篇论文"
                if citation_count > 0:
                    content += f", {citation_count} 引用"
                content += "\n"
        
        # 合作关系统计
        collaboration_edges = [edge for edge in edges if edge.get("type") == "collaborates"]
        
        content += f"\n## 合作统计\n"
        content += f"- 合作关系数: {len(collaboration_edges)}\n"
        
        if len(author_nodes) > 0:
            avg_collaborators = len(collaboration_edges) * 2 / len(author_nodes)
            content += f"- 平均合作伙伴数: {avg_collaborators:.2f}\n"
        
        # 显示主要合作关系
        if collaboration_edges:
            content += f"\n## 主要合作关系\n"
            
            # 按合作强度排序
            collaboration_edges.sort(
                key=lambda x: x.get("properties", {}).get("papers_count", 0),
                reverse=True
            )
            
            for i, edge in enumerate(collaboration_edges[:10], 1):
                source_id = edge.get("source", "")
                target_id = edge.get("target", "")
                properties = edge.get("properties", {})
                papers_count = self._safe_get_int(properties, "papers_count")
                
                # 查找对应的作者名称
                source_name = "Unknown"
                target_name = "Unknown"
                
                for node in author_nodes:
                    if node.get("id") == source_id:
                        source_name = self._safe_get_str(node, "label", "Unknown")
                    elif node.get("id") == target_id:
                        target_name = self._safe_get_str(node, "label", "Unknown")
                
                content += f"{i}. **{source_name}** ↔ **{target_name}**"
                if papers_count > 0:
                    content += f" (合作论文: {papers_count} 篇)"
                content += "\n"
        
        return content
