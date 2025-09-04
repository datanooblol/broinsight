# Version History

## v0.1.1 (Current - Pre-Launch)

### Phase 2 Complete: Reliability & User Guidance ✅
- **Dynamic Flow Architecture**: Sophisticated flow-based system with conditional routing
- **3-Way Intelligent Routing**: Organize action routes to query/guide/default based on user intent
- **Error Handling & Retry System**: Automatic SQL error detection and retry with up to 3 attempts
- **Fallback Mechanism**: Graceful degradation to conversational help when retries fail
- **Guided Questions**: Smart routing to help users discover what they can ask about their data
- **Empty Result Detection**: Handles successful queries that return no data with user feedback
- **Complete Error Coverage**: All actions have comprehensive error handling and logging

### Technical Improvements
- Fixed retry logic bug (was allowing n+1 attempts instead of n)
- Added missing error handling to GuideQuestion and Organize actions
- Enhanced session logging with empty result detection
- Improved user experience for all failure scenarios
- Production-ready reliability across entire pipeline

### Flow Architecture
```
Start → UserInput → Organize → [3-way intelligent routing]
                      ├─ "guide" → GuideQuestion → UserInput (loop)
                      ├─ "select_metadata" → SelectMetadata → GenerateSQL → Retrieve → [error handling]
                      │                                                        ├─ retry → GenerateSQL (up to 3x)
                      │                                                        └─ fallback → Chat → UserInput
                      └─ "default" → Chat → UserInput (loop)
```

### Next: Phase 3 Planning
- Session inspection and audit trails
- Query execution history and performance monitoring
- Advanced metadata exploration tools

## v0.1.0

### Phase 1 Complete: Core Agent ✅
- Basic BroInsight agent for Jupyter Lab
- One-shot Q&A with `ask()` method
- Interactive chat sessions with `chat()` method
- Natural language to SQL conversion
- Conversational data insights
- Happy path functionality working

### Initial Release Features
- Core flow-based architecture using broflow
- Basic actions: Organize, SelectMetadata, GenerateSQL, Retrieve, Chat
- Metadata system with YAML-based table descriptions
- LLM-agnostic design with brollm integration
- Prompt hub with specialized system prompts