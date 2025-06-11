Collaboration Mode Example:
User Query: "Find some latest research on large language models in code generation"


Agent Processing Flow:
├── 1. Understanding Query Intent
│   ├── Topic: Large Language Models + Code Generation
│   ├── Time: Latest (Last 2 years)
│   ├── Type: Research Papers
│   └── Goal: Comprehensive Understanding
├── 2. Formulating Tool Call Strategy
│   ├── First use semantic_search_papers to get relevant papers
│   ├── Then use get_research_trends to analyze trends
│   ├── Finally use get_citation_network to analyze influence
│   └── May need extract_keywords to extract key concepts
├── 3. Execute Tool Calls
│   ├── Parallel tool calls
│   ├── Handle tool dependencies
│   ├── Error handling and retry
│   └── Result collection and validation
├── 4. Result Analysis and Integration
│   ├── Identify important papers and authors
│   ├── Analyze research trends and directions
│   ├── Discover research gaps and opportunities
│   └── Evaluate technology maturity
└── 5. Generate Final Answer
    ├── Structured summary
    ├── Key findings highlighted
    ├── Specific paper recommendations
    └── Further research suggestions