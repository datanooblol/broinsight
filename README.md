# BroInsight

An LLM-agnostic data analysis agent that helps people analyze their own data through natural language conversations.

## Mission

Most people have data but lack the analytics or coding skills to extract meaningful insights. BroInsight bridges this gap by providing an intelligent agent that understands business questions and translates them into data analysis - no SQL or programming knowledge required.

## How It Works

BroInsight uses a sophisticated **flow-based architecture** with dynamic routing and intelligent error recovery:

### Flow Architecture
```
Start → UserInput → Organize → [3-way intelligent routing]
                      ├─ "guide" → GuideQuestion → UserInput (loop)
                      ├─ "select_metadata" → SelectMetadata → GenerateSQL → Retrieve → [error handling]
                      │                                                        ├─ retry → GenerateSQL (up to 3x)
                      │                                                        └─ fallback → Chat → UserInput
                      └─ "default" → Chat → UserInput (loop)
```

### Core Actions
1. **UserInput** - Handles input modes (ask/chat) and exit detection
2. **Organize** - Intelligent 3-way routing (query/guide/default) based on user intent
3. **GuideQuestion** - Provides data exploration suggestions and help
4. **SelectMetadata** - Identifies relevant tables from available data
5. **GenerateSQL** - Converts natural language to SQL with error context
6. **Retrieve** - Executes queries with retry mechanism and graceful fallback
7. **Chat** - Provides conversational insights and answers

## Key Features

- **LLM-Agnostic**: Works with any LLM (OpenAI, Anthropic, local models)
- **Natural Language**: Ask questions in plain English
- **Metadata-Driven**: Understands your data structure automatically
- **Conversational**: Maintains context across multiple questions
- **Jupyter-Ready**: Designed for data science workflows
- **Dynamic Routing**: Intelligent flow control based on user intent and processing results
- **Error Recovery**: Automatic SQL retry with up to 3 attempts and graceful fallback
- **User Guidance**: Built-in help system for data exploration

## Development Roadmap

### Phase 1: Core Agent ✅ (v0.1.0)
- ✅ Basic BroInsight agent for Jupyter Lab
- ✅ One-shot Q&A with `ask()` method
- ✅ Interactive chat sessions with `chat()` method
- ✅ Natural language to SQL conversion
- ✅ Conversational data insights
- ✅ Happy path functionality working

### Phase 2: Reliability & User Guidance ✅ (v0.1.1)
- ✅ SQL error retry mechanism with fallback
- ✅ Graceful failure recovery and user-friendly error messages
- ✅ Guided questions and data exploration assistance
- ✅ Enhanced routing with help/suggestion system
- ✅ Dynamic flow control with conditional routing
- ✅ Comprehensive error handling across all actions
- ✅ Empty result detection and user feedback
- ✅ Complete session logging with DuckDB

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
from broinsight import BroInsight, Shared
from brollm import OpenAIModel  # or your preferred LLM

# Initialize your LLM
model = OpenAIModel(api_key="your-key")

# Create shared state with your question
shared = Shared(model=model)
shared.messages = [model.UserMessage("What's the average customer age?")]

# Process the question
result = BroInsight.chat(shared)

# View the conversation
for msg in result.messages:
    print(f"{msg['role']}: {msg['content']}")
```

## Requirements

- Python 3.12+
- pandas>=2.3.2
- duckdb>=1.3.2
- pydantic>=2.11.7
- brollm>=0.1.2 (LLM interface)
- broflow>=0.1.5 (workflow engine)
- broprompt>=0.1.5 (prompt management)

## Contributing

BroInsight is in active development. We welcome contributions that help make data analysis more accessible to everyone.

## License

See LICENSE file for details.
