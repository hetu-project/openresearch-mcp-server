# src/tools/network_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool,TextContent
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
from src.models.data_models import NetworkAnalysis, NetworkNode, NetworkEdge
from src.utils.error_handler import handle_tool_error  

logger = structlog.get_logger()

class NetworkTools:
    """网络分析工具 - MVP版本"""
    
    def __init__(self, go_client: GoServiceClient, data_processor: DataProcessor):
        self.go_client = go_client
        self.data_processor = data_processor
    
    def get_tools(self) -> List[Tool]:
        """获取工具定义"""
        return [
            Tool(
                name="get_citation_network",
                description="获取论文引用网络",
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
                            "enum": ["forward", "backward", "both"],
                            "default": "both",
                            "description": "引用方向"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 200,
                            "default": 50,
                            "description": "最大节点数"
                        }
                    },
                    "required": ["seed_papers"]
                }
            ),
            Tool(
                name="get_collaboration_network",
                description="获取作者合作网络",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "authors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "作者ID或名称列表"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "时间范围，如'2020-2024'"
                        }
                    },
                    "required": ["authors"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_citation_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取引用网络工具"""
        seed_papers = arguments["seed_papers"]
        depth = arguments.get("depth", 2)
        direction = arguments.get("direction", "both")
        max_nodes = arguments.get("max_nodes", 50)
        
        logger.info(
            "Getting citation network",
            seed_papers=seed_papers,
            depth=depth,
            direction=direction
        )
        
        try:
            raw_result = await self.go_client.get_citation_network(
                seed_papers=seed_papers,
                depth=depth,
                direction=direction,
                max_nodes=max_nodes
            )
            
            # 解析网络数据
            network = self._parse_network_data(raw_result)
            
            content = self._format_citation_network(network, seed_papers)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            return [TextContent(type="text", text=f"获取引用网络失败: {str(e)}")]
    
    @handle_tool_error
    async def get_collaboration_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取合作网络工具"""
        authors = arguments["authors"]
        time_range = arguments.get("time_range")
        
        logger.info("Getting collaboration network", authors=authors, time_range=time_range)
        
        try:
            raw_result = await self.go_client.get_collaboration_network(
                authors=authors,
                time_range=time_range
            )
            
            # 解析网络数据
            network = self._parse_network_data(raw_result)
            
            content = self._format_collaboration_network(network, authors)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get collaboration network failed", error=str(e))
            return [TextContent(type="text", text=f"获取合作网络失败: {str(e)}")]
    
    def _parse_network_data(self, raw_data: Dict[str, Any]) -> NetworkAnalysis:
        """解析网络数据"""
        # 解析节点
        nodes = []
        for raw_node in raw_data.get("nodes", []):
            node = NetworkNode(
                id=raw_node["id"],
                label=raw_node["label"],
                type=raw_node["type"],
                properties=raw_node.get("properties", {})
            )
            nodes.append(node)
        
        # 解析边
        edges = []
        for raw_edge in raw_data.get("edges", []):
            edge = NetworkEdge(
                source=raw_edge["source"],
                target=raw_edge["target"],
                weight=raw_edge.get("weight", 1.0),
                edge_type=raw_edge["edge_type"]
            )
            edges.append(edge)
        
        return NetworkAnalysis(
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges)
        )
    
    def _format_citation_network(self, network: NetworkAnalysis, seed_papers: List[str]) -> str:
        """格式化引用网络结果"""
        content = f"# 引用网络分析\n\n"
        content += f"**种子论文**: {len(seed_papers)} 篇\n"
        content += f"**网络规模**: {network.node_count} 个节点, {network.edge_count} 条边\n\n"
        
        # 统计节点类型
        node_types = {}
        for node in network.nodes:
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        content += "## 网络组成\n"
        for node_type, count in node_types.items():
            content += f"- {node_type}: {count} 个\n"
        
        # 显示重要节点
        content += "\n## 重要节点\n"
        paper_nodes = [node for node in network.nodes if node.type == "paper"]
        
        # 按引用数排序（如果有的话）
        paper_nodes.sort(
            key=lambda x: x.properties.get("citation_count", 0),
            reverse=True
        )
        
        for i, node in enumerate(paper_nodes[:10], 1):
            content += f"{i}. **{node.label}**"
            if "citation_count" in node.properties:
                content += f" (引用数: {node.properties['citation_count']})"
            content += "\n"
        
        # 网络统计
        content += f"\n## 网络统计\n"
        content += f"- 平均度数: {network.edge_count * 2 / network.node_count:.2f}\n"
        
        return content
    
    def _format_collaboration_network(self, network: NetworkAnalysis, authors: List[str]) -> str:
        """格式化合作网络结果"""
        content = f"# 合作网络分析\n\n"
        content += f"**核心作者**: {len(authors)} 位\n"
        content += f"**网络规模**: {network.node_count} 个节点, {network.edge_count} 条边\n\n"
        
        # 显示作者节点
        author_nodes = [node for node in network.nodes if node.type == "author"]
        
        content += "## 网络中的作者\n"
        for i, node in enumerate(author_nodes[:20], 1):
            content += f"{i}. **{node.label}**"
            if "paper_count" in node.properties:
                content += f" (论文数: {node.properties['paper_count']})"
            if "collaboration_count" in node.properties:
                content += f" (合作数: {node.properties['collaboration_count']})"
            content += "\n"
        
        # 合作统计
        content += f"\n## 合作统计\n"
        content += f"- 合作关系数: {network.edge_count}\n"
        content += f"- 平均合作伙伴数: {network.edge_count * 2 / network.node_count:.2f}\n"
        
        return content
