# BroInsight

An LLM-agnostic data analysis agent that helps people analyze their own data through natural language conversations.

## Mission

Most people have data but lack the analytics or coding skills to extract meaningful insights. BroInsight bridges this gap by providing an intelligent agent that understands business questions and translates them into data analysis - no SQL or programming knowledge required.

## How It Works

BroInsight uses a flow-based architecture to process your questions:

1. **Organize** - Routes your question (data query vs general chat)
2. **Select Metadata** - Identifies relevant tables from your data
3. **Generate SQL** - Converts your question to SQL query
4. **Retrieve** - Executes the query against your data
5. **Chat** - Provides conversational insights and answers

## Key Features

- **LLM-Agnostic**: Works with any LLM (OpenAI, Anthropic, local models)
- **Natural Language**: Ask questions in plain English
- **Metadata-Driven**: Understands your data structure automatically
- **Conversational**: Maintains context across multiple questions
- **Jupyter-Ready**: Designed for data science workflows

## Development Roadmap

### Phase 1: Core Agent ✅ (v0.1.1)
- ✅ Basic BroInsight agent for Jupyter Lab
- ✅ One-shot Q&A with `ask()` method
- ✅ Interactive chat sessions with `chat()` method
- ✅ Natural language to SQL conversion
- ✅ Conversational data insights
- ✅ Happy path functionality working

### Phase 2: Reliability & Debugging (Current)
- 📋 Error handling for each pipeline stage
- 📋 Graceful failure recovery
- 📋 User-friendly error messages
- 📋 Guided questions based on metadata (chat mode)
- 📋 Session logging with DuckDB

### Phase 3: Transparency & Guidance
- 📋 Session inspection and audit trails
- 📋 Query execution logs
- 📋 Guided questions about your data
- 📋 Metadata exploration assistance

### Phase 4: Visualization
- 📋 Automatic graph generation from results
- 📋 Tool calling with pre-built chart functions
- 📋 Context-aware visualization suggestions

### Phase 5: Advanced Insights
- 📋 Pattern discovery and recommendations
- 📋 Proactive data exploration suggestions
- 📋 Multi-query analysis workflows

### Phase 6: Reporting
- 📋 PDF report generation
- 📋 Combined graphs and narrative insights
- 📋 Shareable analysis summaries

## Quick Start

```python
from broinsight import BroInsight
from brollm import OpenAIModel  # or your preferred LLM

# Initialize your LLM
model = OpenAIModel(api_key="your-key")

# Create BroInsight agent
agent = BroInsight(model)

# One-shot Q&A
messages = agent.ask("What's the average customer age?")
print(messages)  # See the conversation

# Interactive chat session
agent.chat()  # Start conversational mode
```

## Requirements

- Python 3.12+
- pandas
- duckdb
- brollm (LLM interface)
- broflow (workflow engine)
- broprompt (prompt management)

## Contributing

BroInsight is in active development. We welcome contributions that help make data analysis more accessible to everyone.

## License

See LICENSE file for details.
