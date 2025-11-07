# Validation & Confirmation in Agentic Workflows

## Problem Statement

When users provide vague or ambiguous input, routing decisions become unreliable. Instead of guessing intent and potentially frustrating users, we need **clarification loops** to validate understanding before proceeding.

In API-based systems, this requires **session state management** to maintain context across request/response cycles.

## Core Concepts

### 1. Session State-Based Routing
Use session state as the primary routing signal, with LLM classification as fallback for new conversations.

```python
from enum import Enum

class SessionState(Enum):
    INITIAL = "initial"
    WAITING_CLARIFICATION = "waiting_clarification"
    PROCESSING = "processing"
    COMPLETED = "completed"

def route_request(user_input: str, session_state: SessionState, session_id: str = None) -> dict:
    # Rule-based routing for clarification responses
    if session_state == SessionState.WAITING_CLARIFICATION:
        return handle_clarification_response(user_input, session_id)
    
    # LLM-based routing for new conversations
    if session_state == SessionState.INITIAL or not session_id:
        confidence = calculate_confidence(user_input)
        if confidence < 0.7:
            return create_clarification_session(user_input)
        else:
            return process_direct_query(user_input)
```

### 2. Hybrid Routing Strategy
- **Rule-based**: Fast, reliable parsing for clarification responses
- **LLM-based**: Intelligent classification for initial requests only
- **Session persistence**: Maintain context across API calls

## Session State Management

### State Transitions
```
INITIAL → WAITING_CLARIFICATION (low confidence input)
INITIAL → PROCESSING (high confidence input)
WAITING_CLARIFICATION → PROCESSING (valid user selection)
WAITING_CLARIFICATION → WAITING_CLARIFICATION (invalid selection, retry)
PROCESSING → COMPLETED (task finished)
```

### API Response Types
```python
class APIResponse(BaseModel):
    type: str  # "success", "needs_clarification", "invalid_selection"
    content: str
    options: list[dict] = []
    session_id: str = None
```

## Clarification Strategies

### Multiple Choice with Session Tracking
Present specific options and track selection in session state.

**API Flow Example:**
```
# Request 1
POST /analyze {"query": "I want to see something about sales"}

# Response 1 (creates session)
{
  "type": "needs_clarification",
  "session_id": "abc123",
  "content": "I can help with sales analysis. What would you like to do?",
  "options": [
    {"id": "trends", "label": "View sales trends and patterns"},
    {"id": "explore", "label": "Get help exploring sales data"},
    {"id": "chat", "label": "Ask general questions about sales"}
  ]
}

# Request 2 (user selects option)
POST /analyze {"query": "1", "session_id": "abc123"}

# Response 2 (processes selection)
{
  "type": "success",
  "content": "Here are your sales trends...",
  "session_id": "abc123"
}
```

## Rule-Based Clarification Parsing

### Fast Pattern Matching
Use simple rules instead of LLM for clarification responses - faster and more reliable.

```python
def parse_clarification_response(user_input: str, available_options: list) -> str:
    text = user_input.lower().strip()
    
    # Direct number selection
    if text in ["1", "2", "3"]:
        option_index = int(text) - 1
        if 0 <= option_index < len(available_options):
            return available_options[option_index]['id']
    
    # Keyword matching
    keyword_map = {
        "analyze": "trends",
        "explore": "explore", 
        "help": "explore",
        "chat": "chat",
        "question": "chat"
    }
    
    for keyword, intent in keyword_map.items():
        if keyword in text:
            return intent
    
    return None  # Invalid selection

def handle_clarification_response(user_input: str, session_id: str) -> dict:
    session_context = get_session_context(session_id)
    selected_option = parse_clarification_response(user_input, session_context.pending_options)
    
    if selected_option:
        # Valid selection - route to handler
        update_session_state(session_id, SessionState.PROCESSING)
        result = route_to_handler(selected_option, session_context.original_query)
        update_session_state(session_id, SessionState.COMPLETED)
        return {"type": "success", "content": result}
    else:
        # Invalid selection - ask again
        return {
            "type": "invalid_selection",
            "content": "Please choose 1, 2, or 3",
            "options": session_context.pending_options
        }
```

## Complete API Flow Examples

### Example 1: Vague Query with Session Tracking
```
# Request 1
POST /analyze {"query": "I need help with my data"}

# System: confidence = 0.3 (Low), creates session
# Response 1
{
  "type": "needs_clarification",
  "session_id": "sess_001",
  "content": "What type of assistance do you need?",
  "options": [
    {"id": "analyze", "label": "Analyze data to find insights"},
    {"id": "explore", "label": "Get suggestions for what to explore"},
    {"id": "chat", "label": "General questions about your dataset"}
  ]
}

# Request 2
POST /analyze {"query": "2", "session_id": "sess_001"}

# System: Rule-based parsing, no LLM needed
# Response 2
{
  "type": "success",
  "content": "Here are some questions you can explore...",
  "session_id": "sess_001"
}
```

### Example 2: Direct High-Confidence Query
```
# Request 1
POST /analyze {"query": "Show me sales trends by region for last quarter"}

# System: confidence = 0.9 (High), process directly
# Response 1
{
  "type": "success",
  "content": "Here's your sales analysis..."
}
```

### Example 3: Invalid Selection Handling
```
# Request 1 (creates clarification session)
POST /analyze {"query": "Something about customers"}

# Response 1 (needs clarification)
{
  "type": "needs_clarification",
  "session_id": "sess_002",
  "options": [...]
}

# Request 2 (invalid selection)
POST /analyze {"query": "not sure", "session_id": "sess_002"}

# System: Rule-based parsing fails
# Response 2 (retry clarification)
{
  "type": "invalid_selection",
  "content": "Please choose 1, 2, or 3",
  "options": [...],
  "session_id": "sess_002"
}

# Request 3 (valid selection)
POST /analyze {"query": "1", "session_id": "sess_002"}

# Response 3 (success)
{
  "type": "success",
  "content": "Here's your customer analysis..."
}
```

## Implementation Pattern

```python
def handle_api_request(user_input: str, session_id: str = None) -> dict:
    # Get current session state
    if session_id:
        session_context = get_session_context(session_id)
        current_state = session_context.state
    else:
        current_state = SessionState.INITIAL
    
    # Rule-based routing for clarification responses
    if current_state == SessionState.WAITING_CLARIFICATION:
        return handle_clarification_response(user_input, session_id)
    
    # LLM-based routing for new conversations
    if current_state == SessionState.INITIAL:
        confidence = calculate_confidence(user_input)
        
        if confidence < 0.7:
            # Create clarification session
            session_id = create_session(user_input)
            options = generate_clarification_options(user_input)
            update_session_state(session_id, SessionState.WAITING_CLARIFICATION, options)
            
            return {
                "type": "needs_clarification",
                "session_id": session_id,
                "options": options
            }
        else:
            # Process directly with high confidence
            result = process_query(user_input)
            return {"type": "success", "content": result}
    
    return {"type": "error", "message": "Invalid session state"}
```

## Performance Benefits

### Rule-Based vs LLM Classification
- **Speed**: Rule parsing ~1ms vs LLM calls ~500-2000ms
- **Cost**: Zero tokens for clarification responses
- **Reliability**: No hallucination on simple selections like "1", "2", "3"
- **Deterministic**: Same input always produces same result

### When to Use Each Approach
- **Rules**: Clarification responses, confirmations, simple selections
- **LLM**: Initial intent classification, complex query understanding

## Best Practices

### Do's
- **Use session state as primary routing signal**
- **Reserve LLM for initial classification only**
- **Provide 2-3 specific options** with clear IDs
- **Handle various selection formats** ("1", "first", "analyze")
- **Store original query** in session for context
- **Implement session cleanup** for completed/expired sessions

### Don'ts
- **Don't use LLM for clarification parsing** - rules are faster and more reliable
- **Don't create sessions for high-confidence queries** - process directly
- **Don't lose session context** between requests
- **Don't make users repeat their original question**
- **Don't get stuck in infinite clarification loops**

## Integration with BroInsight

This pattern extends BroInsight's flow architecture:

```
API Request → [Check Session State]
            ├─ WAITING_CLARIFICATION → Rule-based parsing → Route
            └─ INITIAL → LLM classification → [Confidence Check]
                                            ├─ High → Process directly
                                            └─ Low → Create clarification session
```

### Database Schema
```sql
CREATE TABLE session_contexts (
    session_id VARCHAR(36) PRIMARY KEY,
    state VARCHAR(20) NOT NULL,
    original_query TEXT,
    pending_options JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

The session state acts as a **routing hint** that determines whether to use fast rule-based parsing or intelligent LLM classification, optimizing both performance and user experience.