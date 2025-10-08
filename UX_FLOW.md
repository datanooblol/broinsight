# BroInsight Chat App - User Experience Flow

## Overview
BroInsight provides a conversational interface for non-technical users to analyze their data through natural language questions. The app guides users from data upload to actionable insights without requiring SQL or analytics knowledge.

## Core User Journey

### 1. Data Onboarding
**Goal**: Get users from data upload to first insights quickly

**Experience**:
- Simple drag-and-drop interface for CSV/Excel files
- Alternative: Database connection with connection string
- Progress indicator: "Analyzing your data..." with spinner
- Success confirmation: "Found 244 restaurant transactions with 7 fields"
- Brief table description: "This data tracks customer transactions at your restaurant..."

**Technical**: 
- Auto-detect file format and load data
- Generate metadata profile in background
- Create table description using `table_descriptor` prompt

### 2. Welcome & Question Suggestions
**Goal**: Show immediate value and guide exploration

**Experience**:
- Display business-friendly table description
- Show grouped question suggestions by topic:
  ```
  Revenue Analysis
  - Which day brings in the most revenue?
  - What's the average bill amount for dinner vs lunch?

  Customer Insights  
  - Do male or female customers tip better?
  - How do smokers and non-smokers differ in spending?

  Operations Planning
  - Which days are busiest for staffing?
  - What's the typical party size for different meal times?
  ```

**Technical**:
- Use `guide_question(metadata)` to generate suggestions
- Group by business topics (Revenue, Customer, Operations, etc.)
- No technical metadata shown to users

### 3. Question & Answer Flow
**Goal**: Provide immediate, actionable insights

**Experience**:
- User clicks suggestion OR types free-form question
- Brief loading indicator: "Analyzing..."
- Response format:
  - **Data table** (query results)
  - **Conversational insight** (business interpretation)
  - **Follow-up suggestions** (2-3 related questions)

**Technical**:
- Route question through `generate_sql(metadata, question)`
- Execute SQL query to get data
- Use `chat(data, question)` for conversational insights
- Generate follow-up suggestions based on current context

### 4. Continuous Exploration
**Goal**: Keep users engaged and discovering insights

**Experience**:
- After each answer, suggest related questions
- Build on previous context: "Since males tip better, you might want to know..."
- Allow free-form questions anytime
- Maintain conversation history for context

**Technical**:
- Store conversation history per session
- Use previous Q&A context to generate relevant follow-ups
- Handle intent detection (new question vs follow-up)

## Error Handling & Recovery

### SQL Generation Fails
**Experience**: "I couldn't find that data. Here are some questions I can help with: [suggestions]"
**Technical**: Fallback to `guide_question()` with filtered suggestions

### Query Returns Empty Results
**Experience**: "No data matches that criteria. Here's what I can show you instead: [alternative questions]"
**Technical**: Suggest modified queries or different approaches

### Unclear Question
**Experience**: "I'm not sure what you mean. Did you want to know about: [clarifying options]?"
**Technical**: Use metadata to suggest similar valid questions

## Key UX Principles

### Immediate Value
- Show suggestions right after data upload
- No setup or configuration required
- First insight within 30 seconds

### Progressive Disclosure
- Start simple, reveal complexity gradually
- Hide technical details (SQL, metadata)
- Focus on business value

### Guided Discovery
- Always suggest next steps
- Build on previous questions
- Prevent dead ends

### Conversational
- Natural language throughout
- Feel like talking to a data analyst
- Business-friendly explanations

### Forgiving
- Handle errors gracefully
- Provide alternatives when things fail
- Never leave users stuck

## Technical Workflow Integration

### Core Functions (Independent & Reusable)
1. **Data Profiling**: `field_profile(data)` → metadata
2. **Table Description**: `table_descriptor(metadata)` → business description  
3. **Question Suggestions**: `guide_question(metadata)` → grouped suggestions
4. **SQL Generation**: `generate_sql(metadata, question)` → SQL query
5. **Query Execution**: `execute_query(sql)` → data results
6. **Insight Generation**: `chat(data, question)` → conversational analysis
7. **Visualization**: `chart_builder(data, question)` → interactive charts

### Workflow Orchestration
```
Upload Data → Profile → Describe → Suggest Questions
     ↓
User Question → Generate SQL → Execute → Chat Response → Follow-up Suggestions
     ↑                                        ↓
     ←────────── Continue Conversation ←──────
```

### Session Management
- Store metadata per dataset (avoid recomputing)
- Maintain conversation history
- Cache recent queries for quick re-execution
- Handle multiple datasets per user

## Success Metrics
- **Time to First Insight**: < 30 seconds from upload
- **Questions per Session**: > 3 (indicates engagement)
- **Error Recovery Rate**: > 90% (users continue after errors)
- **User Satisfaction**: "I learned something new about my data"