MCP Tool Design Principles:
├── Single Responsibility Principle
│   ├── Each tool does one thing
│   ├── Clear functional boundaries
│   ├── Easy to test and maintain
│   └── Strong reusability
├── Data-Oriented Principle
│   ├── Return structured data
│   ├── Avoid preset interpretations
│   ├── Maintain data integrity
│   └── Support multi-perspective analysis
├── Composability Principle
│   ├── Tools can be combined
│   ├── Output can be input for other tools
│   ├── Support complex workflows
│   └── Avoid functional duplication
└── Performance First Principle
    ├── Fast response
    ├── Efficient resource utilization
    ├── Support concurrent calls
    └── Graceful degradation


Basic Data Tools:
├── search_papers
│   ├── Input: query conditions, filters, pagination parameters
│   ├── Processing: call Go search API
│   ├── Output: paper list, metadata, statistics
│   └── AI Enhancement: none (handled by Agent)
├── get_paper_details
│   ├── Input: paper ID list
│   ├── Processing: batch fetch paper details
│   ├── Output: complete paper information
│   └── AI Enhancement: none
├── get_citation_network
│   ├── Input: paper ID, network depth, direction
│   ├── Processing: call Go graph analysis API
│   ├── Output: nodes, edges, network statistics
│   └── AI Enhancement: none
└── get_research_trends
    ├── Input: field, time range, metric type
    ├── Processing: call Go analysis API
    ├── Output: time series data, statistical indicators
    └── AI Enhancement: none


Computation Enhancement Tools:
├── calculate_similarity
│   ├── Input: text list, similarity algorithm
│   ├── Processing: vectorization + similarity calculation
│   ├── Output: similarity matrix
│   └── AI Enhancement: semantic vectorization
├── extract_keywords
│   ├── Input: text content, extraction quantity
│   ├── Processing: keyword extraction algorithm
│   ├── Output: keyword list, weights
│   └── AI Enhancement: semantic keyword extraction
├── generate_embeddings
│   ├── Input: text list
│   ├── Processing: call embedding model
│   ├── Output: vector representation
│   └── AI Enhancement: multi-model embedding
└── cluster_documents
    ├── Input: document vectors, clustering parameters
    ├── Processing: clustering algorithm
    ├── Output: clustering results, centroids
    └── AI Enhancement: intelligent cluster number selection