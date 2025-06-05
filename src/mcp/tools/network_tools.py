# src/tools/network_tools.py
from typing import Dict, Any, List
import structlog
from mcp.types import Tool, TextContent
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
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
                description="获取论文引用网络图谱",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_id": {
                            "type": "string",
                            "description": "论文ID"
                        },
                        "depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2,
                            "default": 1,
                            "description": "网络深度"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 50,
                            "default": 20,
                            "description": "最大节点数"
                        }
                    },
                    "required": ["paper_id"]
                }
            ),
            Tool(
                name="get_collaboration_network",
                description="获取作者合作网络图谱",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "作者ID"
                        },
                        "depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2,
                            "default": 1,
                            "description": "网络深度"
                        },
                        "max_nodes": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 50,
                            "default": 20,
                            "description": "最大节点数"
                        }
                    },
                    "required": ["author_id"]
                }
            )
        ]
    
    @handle_tool_error
    async def get_citation_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取引用网络工具"""
        paper_id = arguments["paper_id"]
        depth = arguments.get("depth", 1)
        max_nodes = arguments.get("max_nodes", 20)
        
        logger.info(
            "Getting citation network",
            paper_id=paper_id,
            depth=depth,
            max_nodes=max_nodes
        )
        
        try:
            # 使用Go服务的 /network/paper/:id 接口
            raw_result = await self.go_client.get_citation_network(
                seed_papers=[paper_id],
                depth=depth,
                max_nodes=max_nodes
            )
            
            content = self._format_citation_network(raw_result, paper_id)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get citation network failed", error=str(e))
            return [TextContent(type="text", text=f"获取引用网络失败: {str(e)}")]
    
    @handle_tool_error
    async def get_collaboration_network(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取合作网络工具"""
        author_id = arguments["author_id"]
        depth = arguments.get("depth", 1)
        max_nodes = arguments.get("max_nodes", 20)
        
        logger.info(
            "Getting collaboration network", 
            author_id=author_id,
            depth=depth,
            max_nodes=max_nodes
        )
        
        try:
            # 使用Go服务的 /network/author/:id 接口
            raw_result = await self.go_client.get_collaboration_network(
                authors=[author_id]
            )
            
            content = self._format_collaboration_network(raw_result, author_id)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error("Get collaboration network failed", error=str(e))
            return [TextContent(type="text", text=f"获取合作网络失败: {str(e)}")]
    
    def _format_citation_network(self, raw_result: Dict[str, Any], paper_id: str) -> str:
        """格式化引用网络结果"""
        graph = raw_result.get("graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        content = f"# 论文引用网络分析\n\n"
        content += f"**中心论文ID**: {paper_id}\n"
        content += f"**网络规模**: {len(nodes)} 个节点, {len(edges)} 条边\n\n"
        
        if not nodes:
            content += "未找到网络数据。\n"
            return content
        
        # 找到中心节点（第一个节点通常是中心节点）
        center_node = nodes[0] if nodes else None
        if center_node:
            content += f"## 中心论文\n"
            content += f"**标题**: {center_node.get('label', 'Unknown')}\n"
            if center_node.get('properties', {}).get('citations'):
                content += f"**引用数**: {center_node['properties']['citations']}\n"
            if center_node.get('properties', {}).get('published_at'):
                content += f"**发表时间**: {center_node['properties']['published_at'][:10]}\n"
            content += "\n"
        
        # 统计节点类型
        node_types = {}
        paper_nodes = []
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            if node_type == 'paper':
                paper_nodes.append(node)
        
        content += "## 网络组成\n"
        for node_type, count in node_types.items():
            content += f"- {node_type}: {count} 个\n"
        content += "\n"
        
        # 显示相关论文
        if len(paper_nodes) > 1:  # 排除中心节点
            content += "## 相关论文\n"
            related_papers = paper_nodes[1:11]  # 显示前10个相关论文
            
            for i, node in enumerate(related_papers, 1):
                content += f"{i}. **{node.get('label', 'Unknown Title')}**\n"
                
                properties = node.get('properties', {})
                if properties.get('citations'):
                    content += f"   引用数: {properties['citations']}\n"
                
                # 查找与中心节点的关系
                relation_type = "未知关系"
                for edge in edges:
                    if (edge.get('source') == paper_id and edge.get('target') == node.get('id')) or \
                       (edge.get('target') == paper_id and edge.get('source') == node.get('id')):
                        if edge.get('type') == 'cites':
                            if edge.get('source') == paper_id:
                                relation_type = "被中心论文引用"
                            else:
                                relation_type = "引用中心论文"
                        elif edge.get('type') == 'similar_topic':
                            relation_type = "相似主题"
                        break
                
                content += f"   关系: {relation_type}\n"
                content += "\n"
        
        # 网络统计
        content += f"## 网络统计\n"
        if len(nodes) > 0:
            avg_degree = len(edges) * 2 / len(nodes)
            content += f"- 平均度数: {avg_degree:.2f}\n"
        
        # 边类型统计
        edge_types = {}
        for edge in edges:
            edge_type = edge.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        if edge_types:
            content += "- 关系类型分布:\n"
            for edge_type, count in edge_types.items():
                content += f"  - {edge_type}: {count} 条\n"
        
        return content
    
    def _format_collaboration_network(self, raw_result: Dict[str, Any], author_id: str) -> str:
        """格式化合作网络结果"""
        graph = raw_result.get("graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        content = f"# 作者合作网络分析\n\n"
        content += f"**中心作者ID**: {author_id}\n"
        content += f"**网络规模**: {len(nodes)} 个节点, {len(edges)} 条边\n\n"
        
        if not nodes:
            content += "未找到网络数据。\n"
            return content
        
        # 找到中心节点
        center_node = nodes[0] if nodes else None
        if center_node:
            content += f"## 中心作者\n"
            content += f"**姓名**: {center_node.get('label', 'Unknown')}\n"
            properties = center_node.get('properties', {})
            if properties.get('affiliation'):
                content += f"**机构**: {properties['affiliation']}\n"
            if properties.get('citation_count') is not None:
                content += f"**引用数**: {properties['citation_count']}\n"
            content += "\n"
        
        # 显示合作者
        author_nodes = [node for node in nodes if node.get('type') == 'author']
        if len(author_nodes) > 1:  # 排除中心节点
            content += f"## 合作者网络 ({len(author_nodes)-1}位合作者)\n\n"
            
            collaborators = author_nodes[1:21]  # 显示前20个合作者
            for i, node in enumerate(collaborators, 1):
                content += f"{i}. **{node.get('label', 'Unknown')}**\n"
                
                properties = node.get('properties', {})
                if properties.get('affiliation'):
                    content += f"   机构: {properties['affiliation']}\n"
                if properties.get('citation_count') is not None:
                    content += f"   引用数: {properties['citation_count']}\n"
                
                # 查找合作关系
                collaboration_count = 0
                for edge in edges:
                    if (edge.get('source') == author_id and edge.get('target') == node.get('id')) or \
                       (edge.get('target') == author_id and edge.get('source') == node.get('id')):
                        edge_props = edge.get('properties', {})
                        if edge_props.get('papers_count'):
                            collaboration_count = edge_props['papers_count']
                        break
                
                if collaboration_count > 0:
                    content += f"   合作论文数: {collaboration_count}\n"
                
                content += "\n"
        
        # 合作统计
        content += f"## 合作统计\n"
        content += f"- 合作关系数: {len(edges)}\n"
        
        if len(nodes) > 1:
            avg_collaborators = len(edges) * 2 / len(nodes)
            content += f"- 平均合作伙伴数: {avg_collaborators:.2f}\n"
        
        # 统计合作强度
        collaboration_strengths = []
        for edge in edges:
            props = edge.get('properties', {})
            if props.get('papers_count'):
                collaboration_strengths.append(props['papers_count'])
        
        if collaboration_strengths:
            max_collab = max(collaboration_strengths)
            avg_collab = sum(collaboration_strengths) / len(collaboration_strengths)
            content += f"- 最强合作关系: {max_collab} 篇论文\n"
            content += f"- 平均合作强度: {avg_collab:.1f} 篇论文\n"
        
        return content
