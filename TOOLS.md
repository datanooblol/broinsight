# Amazon Q Approach: Tool Selection and Parameter Extraction

This document demonstrates Amazon Q's best practices for intelligent tool selection and parameter extraction using LLMs.

## Overview

Amazon Q uses a multi-stage approach:
1. **Intent Classification** - Understand what the user wants to do
2. **Tool Selection** - Choose the best tool based on semantic matching
3. **Parameter Extraction** - Extract structured parameters from natural language
4. **Confidence Scoring** - Only proceed if confidence is high enough

## 1. Tool Definition (Rich Metadata)

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @property
    @abstractmethod
    def description(self) -> str: pass
    
    @property
    @abstractmethod
    def category(self) -> str: pass
    
    @property
    @abstractmethod
    def keywords(self) -> list: pass
    
    @property
    @abstractmethod
    def examples(self) -> list: pass
    
    @property
    @abstractmethod
    def parameters(self) -> dict: pass

@tool("query_database")
class QueryDatabaseTool(BaseTool):
    @property
    def name(self): return "query_database"
    
    @property
    def description(self): return "Execute SQL queries to retrieve and analyze data from database tables"
    
    @property
    def category(self): return "data_analysis"
    
    @property
    def keywords(self): return ["query", "sql", "database", "select", "data", "table", "search", "find", "show"]
    
    @property
    def examples(self): 
        return [
            "Show me all customers from New York",
            "What's the total sales by region?", 
            "Find orders above $1000",
            "List all products in electronics category"
        ]
    
    @property
    def parameters(self):
        return {
            "sql": "string - SQL query to execute (required)",
            "limit": "integer - Maximum rows to return (optional, default 100)"
        }
    
    def run(self, sql: str, limit: int = 100, context=None):
        # Execute SQL query
        return f"Executed: {sql} (limit: {limit})"

@tool("calculate")
class CalculatorTool(BaseTool):
    @property
    def name(self): return "calculate"
    
    @property
    def description(self): return "Perform mathematical calculations and arithmetic operations"
    
    @property
    def category(self): return "math"
    
    @property
    def keywords(self): return ["calculate", "math", "add", "subtract", "multiply", "divide", "sum", "average"]
    
    @property
    def examples(self):
        return [
            "What's 15 + 27?",
            "Calculate the average of 10, 20, 30",
            "What's 25% of 200?",
            "Multiply 45 by 8"
        ]
    
    @property
    def parameters(self):
        return {
            "expression": "string - Mathematical expression to calculate (required)"
        }
    
    def run(self, expression: str, context=None):
        try:
            result = eval(expression)  # Simple calculator
            return f"Result: {result}"
        except:
            return "Invalid calculation"
```

## 2. Intent Classification (Stage 1)

```python
class IntentClassifier:
    def __init__(self, llm):
        self.llm = llm
    
    def classify(self, user_input: str) -> str:
        prompt = f"""
        User request: "{user_input}"
        
        Classify the user's intent into one of these categories:
        - data_analysis: querying databases, analyzing data, exploring datasets
        - math: calculations, arithmetic operations, mathematical problems
        - visualization: creating charts, graphs, plots
        - file_operations: reading, writing, managing files
        - general_chat: conversation, questions not requiring tools
        
        Return only the category name.
        """
        
        response = self.llm.run(prompt, [])
        return response.content.strip()

# Example Usage
classifier = IntentClassifier(llm)

# Test cases
print(classifier.classify("Show me sales data for Q1"))  # → data_analysis
print(classifier.classify("What's 25 + 30?"))            # → math
print(classifier.classify("How are you today?"))         # → general_chat
```

## 3. Tool Selection (Stage 2)

```python
class ToolSelector:
    def __init__(self, llm):
        self.llm = llm
    
    def select_tool(self, user_input: str, intent: str) -> dict:
        # Filter tools by category
        available_tools = self.get_tools_by_category(intent)
        
        if len(available_tools) == 0:
            return {"tool": None, "confidence": 0, "reason": "No tools available for this intent"}
        
        if len(available_tools) == 1:
            tool_name = list(available_tools.keys())[0]
            return {"tool": tool_name, "confidence": 95, "reason": "Only one tool matches category"}
        
        # Multiple tools - use semantic matching
        return self.semantic_match(user_input, available_tools)
    
    def get_tools_by_category(self, intent: str) -> dict:
        all_tools = ToolRegistry.list()
        return {name: cls for name, cls in all_tools.items() 
                if cls().category == intent}
    
    def semantic_match(self, user_input: str, candidate_tools: dict) -> dict:
        # Create tool comparison data
        tool_info = []
        for name, tool_class in candidate_tools.items():
            tool = tool_class()
            tool_info.append({
                "name": name,
                "description": tool.description,
                "keywords": tool.keywords,
                "examples": tool.examples
            })
        
        prompt = f"""
        User request: "{user_input}"
        
        Available tools:
        {tool_info}
        
        Which tool best matches the user's request? Consider:
        1. Semantic similarity between request and tool description
        2. Keyword overlap
        3. Similarity to tool examples
        
        Rate your confidence (0-100) and provide reasoning.
        
        Return JSON: {{"tool": "tool_name", "confidence": 85, "reason": "explanation"}}
        """
        
        response = self.llm.run(prompt, [])
        try:
            return json.loads(response.content)
        except:
            return {"tool": None, "confidence": 0, "reason": "Failed to parse response"}

# Example Usage
selector = ToolSelector(llm)

result = selector.select_tool("Show me customers from California", "data_analysis")
print(result)  # {"tool": "query_database", "confidence": 90, "reason": "Request matches database querying"}
```

## 4. Parameter Extraction (Stage 3)

```python
class ParameterExtractor:
    def __init__(self, llm):
        self.llm = llm
    
    def extract_parameters(self, user_input: str, tool_name: str) -> dict:
        # Get tool parameter specification
        tool_class = ToolRegistry.list()[tool_name]
        tool = tool_class()
        
        prompt = f"""
        User request: "{user_input}"
        
        Tool: {tool.name}
        Description: {tool.description}
        
        Parameters:
        {tool.parameters}
        
        Extract parameters from the user request. For missing required parameters, 
        use reasonable defaults or indicate they need clarification.
        
        Return JSON with parameter values:
        """
        
        response = self.llm.run(prompt, [])
        try:
            return json.loads(response.content)
        except:
            return {}

# Example Usage
extractor = ParameterExtractor(llm)

# Test: "Show me customers from California"
params = extractor.extract_parameters(
    "Show me customers from California", 
    "query_database"
)
print(params)  # {"sql": "SELECT * FROM customers WHERE state = 'California'", "limit": 100}

# Test: "What's 15 plus 27?"
params = extractor.extract_parameters(
    "What's 15 plus 27?", 
    "calculate"
)
print(params)  # {"expression": "15 + 27"}
```

## 5. Complete Amazon Q Orchestrator

```python
class AmazonQOrchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.classifier = IntentClassifier(llm)
        self.selector = ToolSelector(llm)
        self.extractor = ParameterExtractor(llm)
        self.confidence_threshold = 70  # Amazon Q standard
    
    def process_request(self, user_input: str) -> dict:
        # Stage 1: Classify Intent
        intent = self.classifier.classify(user_input)
        
        if intent == "general_chat":
            return {"action": "chat", "response": "I can help with data analysis, calculations, and more. What would you like to do?"}
        
        # Stage 2: Select Tool
        tool_selection = self.selector.select_tool(user_input, intent)
        
        if tool_selection["confidence"] < self.confidence_threshold:
            return {
                "action": "clarify",
                "response": f"I'm not sure which tool to use. {tool_selection['reason']} Could you be more specific?"
            }
        
        tool_name = tool_selection["tool"]
        
        # Stage 3: Extract Parameters
        parameters = self.extractor.extract_parameters(user_input, tool_name)
        
        # Stage 4: Execute Tool
        result = self.execute_tool(tool_name, parameters)
        
        return {
            "action": "tool_execution",
            "tool": tool_name,
            "parameters": parameters,
            "confidence": tool_selection["confidence"],
            "result": result
        }
    
    def execute_tool(self, tool_name: str, parameters: dict):
        try:
            tool_class = ToolRegistry.list()[tool_name]
            tool_instance = tool_class()
            return tool_instance.run(**parameters)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

# Example Usage
orchestrator = AmazonQOrchestrator(llm)

# Test various requests
test_cases = [
    "Show me all customers from New York",
    "What's 25% of 400?", 
    "How are you doing today?",
    "Calculate the sum of 10, 20, and 30"
]

for request in test_cases:
    print(f"\nUser: {request}")
    result = orchestrator.process_request(request)
    print(f"Action: {result['action']}")
    if 'result' in result:
        print(f"Result: {result['result']}")
    else:
        print(f"Response: {result['response']}")
```

## 6. Real-World Examples

### Example 1: Database Query
```
User: "Show me all orders above $500 from last month"

Stage 1 (Intent): data_analysis
Stage 2 (Tool): query_database (confidence: 92%)
Stage 3 (Parameters): {
    "sql": "SELECT * FROM orders WHERE amount > 500 AND order_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH)",
    "limit": 100
}
Stage 4 (Result): [Query executed successfully, 47 rows returned]
```

### Example 2: Calculation
```
User: "What's the average of 85, 92, 78, and 96?"

Stage 1 (Intent): math
Stage 2 (Tool): calculate (confidence: 95%)
Stage 3 (Parameters): {
    "expression": "(85 + 92 + 78 + 96) / 4"
}
Stage 4 (Result): "Result: 87.75"
```

### Example 3: Ambiguous Request
```
User: "Help me with data"

Stage 1 (Intent): data_analysis
Stage 2 (Tool): None (confidence: 30%)
Response: "I'm not sure which data tool to use. Could you be more specific about what you want to do with the data? For example: query a database, analyze a file, or create a visualization?"
```

## Key Benefits of Amazon Q Approach

1. **High Accuracy**: Multi-stage filtering reduces wrong tool selection
2. **Confidence Scoring**: Only proceeds when confident, asks for clarification otherwise
3. **Rich Metadata**: Semantic keywords and examples improve matching
4. **Graceful Degradation**: Falls back to conversation when tools aren't appropriate
5. **Extensible**: Easy to add new tools with consistent interface

This approach ensures robust, production-ready tool selection that works reliably across diverse user inputs.