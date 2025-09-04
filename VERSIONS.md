# Version History

## v0.1.1 (Current)

### New Features
- **BroInsight Wrapper Class**: Added user-friendly interface with two interaction modes
  - `ask(question)` - One-shot Q&A mode that returns conversation messages
  - `chat()` - Interactive chat mode for exploratory conversations
- **Dual Mode Support**: Flow now supports both pre-populated questions and interactive input
- **Improved Message Handling**: Fixed conversation flow and message management

### Technical Changes
- Modified `UserInput` action to detect pre-populated questions (one-shot mode)
- Created `BroInsight` wrapper class in `broinsight/broinsight.py`
- Updated `Chat` action for better message handling
- Added proper exports in `__init__.py`

### Phase 1 Complete ✅
- Basic BroInsight agent working in Jupyter Lab
- One-shot Q&A and interactive chat sessions implemented
- Natural language to SQL conversion functional
- Conversational data insights working on happy path

### Next: Phase 2 Planning
- Error handling for each pipeline stage
- Guided questions based on metadata for chat mode
- Graceful failure recovery

## v0.1.0

### Initial Release
- Core flow-based architecture using broflow
- Basic actions: Organize, SelectMetadata, GenerateSQL, Retrieve, Chat
- Metadata system with YAML-based table descriptions
- LLM-agnostic design with brollm integration
- Prompt hub with specialized system prompts