# OpenResearch MCP Server

An AI-powered academic research platform that provides MCP (Model Context Protocol) server capabilities for structuring academic papers into knowledge graphs and enabling automated paper review and generation.

## 🚀 Features

- **Academic Paper Processing**: Structure academic papers into knowledge graphs
- **Automated Research Tools**: AI-powered paper review and generation capabilities
- **MCP Protocol Support**: Full compatibility with Model Context Protocol
- **Go Service Integration**: High-performance backend services written in Go
- **Asynchronous Architecture**: Built with Python asyncio for optimal performance
- **Comprehensive Logging**: Structured logging with detailed error tracking

## 📋 Requirements

- Python 3.10
- Dependencies listed in `requirements.txt`

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/openresearch-mcp-server.git
cd openresearch-mcp-server
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Running the MCP Server

```bash
python src/main.py
```

The server will start and listen for MCP protocol connections via stdio.

### Configuration

The server uses configuration settings from `src/config.py`. Key settings include:

- `server_name`: Name of the MCP server
- Logging configuration
- Service endpoints and timeouts

## 🏗️ Architecture

### Core Components

- **`AcademicMCPServer`**: Main server class handling MCP protocol
- **`GoServiceClient`**: Client for communicating with Go backend services
- **`DataProcessor`**: Handles academic data processing and analysis
- **Tool Registry**: Dynamic tool registration and execution system

### Project Structure

```
openresearch-mcp-server/
├── src/
│   ├── server/
│   │   └── mcp_server.py      # Main MCP server implementation
│   ├── clients/
│   │   └── go_client.py       # Go service client
│   ├── services/
│   │   └── data_processor.py  # Data processing services
│   ├── core/
│   │   └── tools.py           # Tool definitions and registry
│   ├── utils/
│   │   └── logging_config.py  # Logging configuration
│   ├── config.py              # Application configuration
│   └── main.py                # Application entry point
├── scripts/                   # Utility scripts
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Available Tools

The server provides various research tools accessible via MCP protocol:

- **Paper Analysis**: Extract and analyze academic paper content
- **Knowledge Graph Generation**: Convert papers into structured knowledge graphs
- **Research Synthesis**: Automated literature review and synthesis
- **Citation Analysis**: Analyze citation networks and relationships

## 📡 MCP Protocol Support

### Supported Capabilities

- **Tools**: Dynamic tool listing and execution
- **Error Handling**: Comprehensive error reporting and recovery
- **Async Operations**: Full asynchronous operation support

### Tool Execution

Tools are executed via the MCP `call_tool` method:

```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

## 🔍 Logging and Monitoring

The server uses structured logging with the following features:

- **Structured Logs**: JSON-formatted logs with contextual information
- **Error Tracking**: Detailed error reporting with stack traces
- **Performance Monitoring**: Tool execution timing and performance metrics
- **Debug Support**: Configurable log levels for development and production

## 🛡️ Error Handling

Robust error handling includes:

- **Tool Validation**: Verification of tool existence before execution
- **Input Validation**: Argument validation for all tool calls
- **Graceful Degradation**: Proper error responses via MCP protocol
- **Resource Cleanup**: Automatic cleanup of resources on shutdown

## 🔄 Development Workflow

### Running in Development Mode

```bash
# Set development environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/main.py
```

### Testing Tools

```bash
# List available tools
# (via MCP client)

# Execute a specific tool
# (via MCP client with tool parameters)
```

## 📊 Performance Considerations

- **Async Architecture**: Non-blocking I/O operations
- **Connection Pooling**: Efficient Go service client connections
- **Resource Management**: Proper cleanup and resource management
- **Error Recovery**: Automatic recovery from transient failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the code comments for implementation details

## 🔮 Roadmap

- [ ] Enhanced paper parsing capabilities
- [ ] Additional knowledge graph formats
- [ ] Real-time collaboration features
- [ ] Advanced citation analysis
- [ ] Integration with more academic databases

## ⚡ Performance Tips

1. **Connection Management**: The server uses async context managers for efficient resource handling
2. **Tool Caching**: Frequently used tools benefit from result caching
3. **Batch Processing**: Process multiple papers in batches for better performance

---

**Built with ❤️ for the academic research community**
