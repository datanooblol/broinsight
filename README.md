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

### Phase 2.5: Separated Concerns Architecture ✅ (v0.1.2-0.1.3)
- ✅ **DataCatalog**: Universal data ingestion (pandas, local CSV, S3)
- ✅ **BroInsight**: Clean LLM interface with specialized methods
- ✅ **Automatic Profiling**: Data quality assessment and metadata generation
- ✅ **Caching System**: Profile once, use multiple times
- ✅ **Relationship Management**: Multi-table analysis support
- ✅ **Multiple Output Formats**: SQL metadata, guidance metadata, DQ profiles

### Phase 3: Transparency & User Feedback 🔄 (v0.2.0)
- 📋 Session inspection and audit trails
- 📋 Query execution history and performance monitoring
- 📋 User feedback collection system
- 📋 Plugin architecture for extensibility
- 📋 Configuration-driven behavior

### Phase 4: Visualization & Advanced Analytics
- 📋 Enhanced chart generation with context-aware suggestions
- 📋 Pattern discovery and anomaly detection
- 📋 Multi-LLM orchestration for specialized tasks
- 📋 Real-time data streaming support

### Phase 5: Enterprise Integration
- 📋 BI tool integration (Tableau, PowerBI, Looker)
- 📋 Data platform connectors (Snowflake, Databricks, BigQuery)
- 📋 MLOps pipeline integration
- 📋 Workflow orchestration (Airflow, Prefect)

### Phase 6: Collaborative Analytics
- 📋 Multi-user collaboration features
- 📋 Conversational data governance
- 📋 Cross-team integration (Slack, Teams)
- 📋 Automated documentation generation

## Quick Start

### Simple Analysis with DataCatalog + BroInsight

```python
import pandas as pd
from broinsight.utils.data_catalog import DataCatalog
from broinsight.broinsight import BroInsight
from brollm import OpenAIModel  # or your preferred LLM

# Setup
model = OpenAIModel(api_key="your-key")
broinsight = BroInsight(model)
catalog = DataCatalog()

# Load and profile your data
df = pd.read_csv("your_data.csv")
catalog.register("sales", df, "Sales transaction data")
catalog.profile_tables(["sales"])

# Add field descriptions for better analysis
from broinsight.utils.data_spec import FieldDescription, FieldDescriptions
descriptions = FieldDescriptions(descriptions=[
    FieldDescription(field_name="amount", description="Transaction amount in USD"),
    FieldDescription(field_name="customer_id", description="Unique customer identifier")
])
catalog.add_field_descriptions("sales", descriptions)

# Ask questions about your data
metadata = catalog.to_sql_metadata("sales")
response = broinsight.generate_sql(metadata, "What's the average transaction amount?")
print(response['content'])

# Get data quality insights
profile = catalog.to_dq_profile("sales")
quality_response = broinsight.assess_data_quality(profile, "Is my data ready for analysis?")
print(quality_response['content'])

# Get question suggestions
guide_metadata = catalog.to_guide_metadata("sales")
suggestions = broinsight.suggest_questions(guide_metadata, "I'm a sales manager")
print(suggestions['content'])
```

### Multi-Table Analysis

```python
# Load multiple related tables
catalog.register("customers", customers_df, "Customer information")
catalog.register("orders", orders_df, "Order transactions")

# Define relationships
catalog.add_relationship("orders", "customer_id", "customers", "customer_id")

# Profile all tables
catalog.profile_tables(["customers", "orders"])

# Analyze across tables
metadata = catalog.to_sql_metadata(["customers", "orders"])
response = broinsight.generate_sql(metadata, "Which customers have the highest total order value?")
```

## Requirements

- Python 3.12+
- pandas>=2.3.2
- duckdb>=1.3.2
- pydantic>=2.11.7
- brollm>=0.1.2 (LLM interface)
- broflow>=0.1.5 (workflow engine)
- broprompt>=0.1.5 (prompt management)

## Architecture

### Separated Concerns Design

**DataCatalog** - Universal data management
- Ingests pandas DataFrames, local files, S3 data
- Automatic profiling with data quality assessment
- Relationship management for multi-table analysis
- Multiple metadata output formats for different use cases

**BroInsight** - LLM-powered analysis interface
- Specialized methods for different analysis tasks
- Clean separation between data management and AI logic
- Pluggable architecture for future enhancements

**Prompt Hub** - Specialized prompts for each capability
- SQL generation with complex query support
- Data quality assessment and recommendations
- Question guidance and exploration assistance
- Chart generation with context-aware suggestions

## Current Status

BroInsight v0.1.3 represents a mature, production-ready data analysis agent with separated concerns architecture. The system is designed for maintainability and extensibility, with clear interfaces between data management (DataCatalog) and AI analysis (BroInsight).

**Ready for Production Use:**
- Comprehensive error handling and retry mechanisms
- Data quality assessment and profiling
- Multi-table relationship support
- LLM-agnostic design for flexibility

**User Feedback Phase:**
We're currently collecting user feedback to inform Phase 3 development decisions. The architecture is designed to evolve based on real-world usage patterns while maintaining backward compatibility.

## Contributing

BroInsight is in active development. We welcome contributions that help make data analysis more accessible to everyone.

## License

MIT License - see LICENSE file for details.
