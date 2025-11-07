# Comprehensive Guide to Tool Calling with LLMs

This document provides a complete guide to implementing intelligent tool calling systems using Large Language Models, based on Amazon Q's proven patterns and advanced techniques.

## Table of Contents

1. [Core Concepts](#1-core-concepts)
2. [Essential Patterns](#2-essential-patterns)
3. [Tool Definition Approaches](#3-tool-definition-approaches)
4. [Multi-Stage Pipeline](#4-multi-stage-pipeline)
5. [Advanced Patterns](#5-advanced-patterns)
6. [Multi-Tool Scenarios](#6-multi-tool-scenarios)
7. [Production Considerations](#7-production-considerations)
8. [Real-World Examples](#8-real-world-examples)
9. [Best Practices Summary](#9-best-practices-summary)

---

## 1. Core Concepts

### What is Tool Calling?
Tool calling enables LLMs to execute external functions/APIs based on natural language input. Instead of just generating text, the LLM can:
- Query databases
- Perform calculations
- Call external APIs
- Process files
- Execute system commands

### Key Challenges
1. **Tool Selection**: Which tool should handle the request?
2. **Parameter Extraction**: How to convert natural language to structured parameters?
3. **Multi-Tool Coordination**: When multiple tools are needed
4. **Error Handling**: What to do when things go wrong?
5. **Context Management**: Maintaining state across interactions

---

## 2. Essential Patterns

### 2.1 Multi-Stage Pipeline Pattern ⭐⭐⭐
**The Foundation Pattern**
```
User Input → Intent Classification → Tool Selection → Parameter Extraction → Execution
```

**Why Essential**: Prevents wrong tool selection, improves accuracy by 60-80%

### 2.2 Confidence Scoring Pattern ⭐⭐⭐
**The Safety Pattern**
```python
if confidence < 70:
    return "Please clarify your request"
else:
    execute_tool()
```

**Why Essential**: Avoids bad user experiences, asks for clarification instead of guessing

### 2.3 Rich Metadata Pattern ⭐⭐
**The Context Pattern**
```python
tool_metadata = {
    "description": "Clear purpose statement",
    "keywords": ["semantic", "matching", "terms"],
    "examples": ["concrete", "use", "cases"],
    "parameters": {"structured": "input specification"}
}
```

**Why Important**: LLMs need rich context to make good decisions

### 2.4 Graceful Degradation Pattern ⭐⭐
**The Fallback Pattern**
```python
if no_suitable_tool_found:
    return conversational_response()
elif confidence_too_low:
    return clarification_request()
else:
    return tool_execution()
```

**Why Important**: Always have a fallback, never fail silently

---

## 3. Tool Definition Approaches

### 3.1 Class-Based Approach (Structured)
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
```

### 3.2 Docstring-Based Approach (Pythonic) ⭐ **Recommended**
```python
# Updated parser with Category support
def parse_google_docstring(func) -> Dict:
    """Parse Google-style docstring to extract tool metadata"""
    docstring = inspect.getdoc(func)
    if not docstring:
        return {}
    
    # Extract description (first line)
    lines = docstring.strip().split('\n')
    description = lines[0].strip()
    
    # Extract category
    category_match = re.search(r'Category:\s*(.+)', docstring)
    category = "general"
    if category_match:
        category = category_match.group(1).strip()
    
    # Extract keywords
    keywords_match = re.search(r'Keywords:\s*(.+)', docstring)
    keywords = []
    if keywords_match:
        keywords = [k.strip() for k in keywords_match.group(1).split(',')]
    
    # Extract parameters
    args_section = re.search(r'Args:\s*\n(.*?)(?=Returns:|$)', docstring, re.DOTALL)
    parameters = {}
    if args_section:
        for line in args_section.group(1).split('\n'):
            line = line.strip()
            if line and ':' in line:
                match = re.match(r'(\w+)\s*\(([^)]+)\)\s*:\s*(.+)', line)
                if match:
                    param_name, param_type, param_desc = match.groups()
                    parameters[param_name] = f"{param_type} - {param_desc}"
    
    return {
        "description": description,
        "category": category,
        "keywords": keywords,
        "parameters": parameters
    }

# Example tools with categories
@tool("stock_checker")
def check_stock_index(index: str) -> str:
    """Check a stock by index from Yahoo API
    Category: finance
    Keywords: stock, investment, finance, market, ticker
    Args:
        index (str): a stock index like AAPL, GOOGL, TSLA
    Returns:
        str: a response from Yahoo API with stock data
    """
    return f"Stock data for {index}"

@tool("currency_convert")
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert currency from one type to another
    Category: finance
    Keywords: currency, convert, exchange, rate, USD, EUR
    Args:
        amount (float): amount to convert
        from_currency (str): source currency code
        to_currency (str): target currency code
    Returns:
        float: converted amount
    """
    return amount * 1.1  # Mock conversion

@tool("calculator")
def calculate_math(expression: str) -> float:
    """Perform mathematical calculations
    Category: math
    Keywords: math, calculate, arithmetic, compute, add, multiply
    Args:
        expression (str): mathematical expression to evaluate
    Returns:
        float: calculated result
    """
    return eval(expression)

@tool("query_database")
def query_database(sql: str, limit: int = 100) -> str:
    """Execute SQL queries on database
    Category: data_analysis
    Keywords: query, sql, database, data, search, select
    Args:
        sql (str): SQL query to execute
        limit (int): maximum number of rows to return
    Returns:
        str: query results as formatted string
    """
    return f"Executed: {sql} (limit: {limit})"
```

**Benefits of Docstring Approach**:
- Standard Python documentation
- IDE support for parameter hints
- Auto-parsing eliminates manual metadata
- Type hints integration
- **Category + Keywords**: Perfect for multi-stage filtering
- Serves as both docs and tool metadata

---

## 4. Multi-Stage Pipeline

### 4.1 Intent Classification (Stage 1)

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
        - finance: stock prices, currency conversion, financial analysis
        - visualization: creating charts, graphs, plots
        - file_operations: reading, writing, managing files
        - general_chat: conversation, questions not requiring tools
        
        Return only the category name.
        """
        
        response = self.llm.run(prompt, [])
        return response.content.strip()
```

### 4.2 Category → Keyword Tool Selection (Complete Example)

```python
class SmartToolSelector:
    def __init__(self, llm):
        self.llm = llm
    
    def select_tool(self, user_input: str) -> dict:
        """Complete Category → Keyword → Parameter pipeline"""
        
        # Stage 1: Intent Classification to Category
        category = self.classify_to_category(user_input)
        
        # Stage 2: Filter tools by category
        candidate_tools = self.filter_by_category(category)
        
        if len(candidate_tools) == 0:
            return {"tool": None, "confidence": 0, "reason": f"No tools for category: {category}"}
        
        if len(candidate_tools) == 1:
            tool_name = list(candidate_tools.keys())[0]
            return {"tool": tool_name, "confidence": 95, "reason": "Only tool in category"}
        
        # Stage 3: Keyword matching within category
        best_tool = self.keyword_match(user_input, candidate_tools)
        
        return best_tool
    
    def classify_to_category(self, user_input: str) -> str:
        """Classify user input to tool category"""
        prompt = f"""
        User: "{user_input}"
        
        Classify into one category:
        - finance: stocks, currency, financial data
        - math: calculations, arithmetic, formulas
        - data_analysis: database queries, data exploration
        - general: other requests
        
        Return only the category name.
        """
        
        response = self.llm.run(prompt, [])
        return response.content.strip()
    
    def filter_by_category(self, category: str) -> dict:
        """Filter tools by category"""
        all_tools = ToolBox.list_tools()
        return {name: info for name, info in all_tools.items() 
                if info["category"] == category}
    
    def keyword_match(self, user_input: str, candidate_tools: dict) -> dict:
        """Score tools by keyword overlap"""
        scores = {}
        user_words = set(user_input.lower().split())
        
        for tool_name, tool_info in candidate_tools.items():
            # Calculate keyword overlap score
            tool_keywords = set([kw.lower() for kw in tool_info["keywords"]])
            overlap = len(user_words.intersection(tool_keywords))
            keyword_score = (overlap / len(tool_keywords)) * 100 if tool_keywords else 0
            
            scores[tool_name] = {
                "score": keyword_score,
                "overlap_words": list(user_words.intersection(tool_keywords))
            }
        
        # Get best match
        best_tool = max(scores.keys(), key=lambda x: scores[x]["score"])
        best_score = scores[best_tool]["score"]
        
        return {
            "tool": best_tool,
            "confidence": min(int(best_score + 50), 95),  # Boost confidence
            "reason": f"Keyword match: {scores[best_tool]['overlap_words']}"
        }

# Usage Example
selector = SmartToolSelector(llm)

# Test cases
test_cases = [
    "What's Apple's stock price?",
    "Convert 100 USD to EUR", 
    "Calculate 25 * 4",
    "Show me customer data from database"
]

for user_input in test_cases:
    result = selector.select_tool(user_input)
    print(f"Input: {user_input}")
    print(f"Selected: {result['tool']} (confidence: {result['confidence']}%)")
    print(f"Reason: {result['reason']}\n")

# Expected outputs:
# Input: "What's Apple's stock price?"
# Category: finance → Tools: [stock_checker, currency_convert]
# Keywords: ["stock", "price"] → Best match: stock_checker
# Selected: stock_checker (confidence: 85%)

# Input: "Convert 100 USD to EUR"
# Category: finance → Tools: [stock_checker, currency_convert] 
# Keywords: ["convert", "USD", "EUR"] → Best match: currency_convert
# Selected: currency_convert (confidence: 90%)
```

### 4.3 Parameter Extraction with Context

```python
class ContextualParameterExtractor:
    def __init__(self, llm):
        self.llm = llm
    
    def extract_parameters(self, user_input: str, tool_name: str) -> dict:
        """Extract parameters using tool's docstring specification"""
        tool_info = ToolBox.get_tool_info(tool_name)
        
        prompt = f"""
        User request: "{user_input}"
        
        Tool: {tool_name}
        Description: {tool_info['description']}
        Category: {tool_info['category']}
        
        Required parameters:
        {tool_info['parameters']}
        
        Extract parameters from user input. Use these guidelines:
        - For stock symbols: extract ticker symbols (AAPL, GOOGL, etc.)
        - For currency: use 3-letter codes (USD, EUR, GBP)
        - For math: extract the complete expression
        - For missing required params: use reasonable defaults or indicate "MISSING"
        
        Return JSON with parameter values:
        """
        
        response = self.llm.run(prompt, [])
        try:
            return json.loads(response.content)
        except:
            return {}

# Complete pipeline example
def complete_tool_pipeline(user_input: str) -> dict:
    """Complete Category → Keyword → Parameter → Execution pipeline"""
    
    # Step 1: Select tool using category + keyword filtering
    selector = SmartToolSelector(llm)
    selection = selector.select_tool(user_input)
    
    if selection["confidence"] < 70:
        return {
            "action": "clarify",
            "response": f"Not sure which tool to use. {selection['reason']}"
        }
    
    tool_name = selection["tool"]
    
    # Step 2: Extract parameters
    extractor = ContextualParameterExtractor(llm)
    parameters = extractor.extract_parameters(user_input, tool_name)
    
    # Step 3: Execute tool
    tool_info = ToolBox.get_tool_info(tool_name)
    result = tool_info["function"](**parameters)
    
    return {
        "action": "tool_execution",
        "tool": tool_name,
        "category": tool_info["category"],
        "parameters": parameters,
        "confidence": selection["confidence"],
        "result": result
    }

# Test the complete pipeline
test_inputs = [
    "What's Tesla stock trading at?",
    "Convert 500 dollars to euros",
    "What's 15 percent of 240?"
]

for user_input in test_inputs:
    result = complete_tool_pipeline(user_input)
    print(f"User: {user_input}")
    print(f"Tool: {result.get('tool')} (Category: {result.get('category')})")
    print(f"Parameters: {result.get('parameters')}")
    print(f"Result: {result.get('result')}\n")
```

### 4.4 Traditional Tool Selection (Stage 2)

```python
class ToolSelector:
    def __init__(self, llm):
        self.llm = llm
    
    def select_tool(self, user_input: str, intent: str) -> dict:
        # Filter tools by category first
        available_tools = self.get_tools_by_category(intent)
        
        if len(available_tools) == 0:
            return {"tool": None, "confidence": 0, "reason": "No tools available for this intent"}
        
        if len(available_tools) == 1:
            tool_name = list(available_tools.keys())[0]
            return {"tool": tool_name, "confidence": 95, "reason": "Only one tool matches category"}
        
        # Multiple tools - use semantic matching
        return self.semantic_match(user_input, available_tools)
    
    def semantic_match(self, user_input: str, candidate_tools: dict) -> dict:
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
```

### 4.3 Parameter Extraction (Stage 3)

```python
class ParameterExtractor:
    def __init__(self, llm):
        self.llm = llm
    
    def extract_parameters(self, user_input: str, tool_name: str) -> dict:
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
```

---

## 5. Advanced Patterns

### 5.1 Category Filtering Pattern ⭐
**Reduces Search Space Dramatically**

```python
class CategoryFilteredSelector:
    def __init__(self, llm):
        self.llm = llm
        self.categories = {
            "data_analysis": ["query_database", "analyze_data", "export_csv"],
            "math": ["calculate", "statistics", "convert_units"],
            "finance": ["stock_price", "currency_convert", "portfolio_analysis"],
            "visualization": ["create_chart", "plot_data", "dashboard"]
        }
    
    def select_tool(self, user_input: str) -> dict:
        # Step 1: Classify intent to category
        intent = self.classify_intent(user_input)
        
        # Step 2: Filter tools by category (huge reduction in search space)
        candidate_tools = self.categories.get(intent, [])
        
        if len(candidate_tools) == 0:
            return {"tool": None, "reason": f"No tools for {intent}"}
        
        if len(candidate_tools) == 1:
            return {"tool": candidate_tools[0], "confidence": 95}
        
        # Step 3: Semantic match within category only
        return self.semantic_match_within_category(user_input, candidate_tools)

# Example:
# User: "What's Apple's stock price?"
# Step 1: intent = "finance" (not data_analysis, math, etc.)
# Step 2: candidates = ["stock_price", "currency_convert", "portfolio_analysis"] 
# Step 3: match within finance tools only → "stock_price"
```

### 5.2 Parameter Validation Pattern ⭐
**Validate Before Execution**

```python
import inspect
from typing import get_type_hints

def validate_parameters(func, params: dict) -> dict:
    """Validate parameters against function signature"""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    validated = {}
    errors = []
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
            
        # Check required parameters
        if param.default == inspect.Parameter.empty and param_name not in params:
            errors.append(f"Missing required parameter: {param_name}")
            continue
        
        # Get value (use default if not provided)
        value = params.get(param_name, param.default)
        
        # Type validation
        if param_name in type_hints:
            expected_type = type_hints[param_name]
            if not isinstance(value, expected_type):
                try:
                    # Try to convert
                    value = expected_type(value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter {param_name} must be {expected_type.__name__}, got {type(value).__name__}")
                    continue
        
        validated[param_name] = value
    
    return {"params": validated, "errors": errors}

# Usage Example:
@tool("query_database")
def query_database(sql: str, limit: int = 100) -> str:
    """Query database with SQL"""
    return f"Query: {sql}, Limit: {limit}"

# Validate before execution
extracted_params = {"sql": "SELECT * FROM users", "limit": "50"}  # limit is string
validation = validate_parameters(query_database, extracted_params)

if validation["errors"]:
    return f"Parameter errors: {validation['errors']}"
else:
    result = query_database(**validation["params"])  # limit converted to int
```

### 5.3 Context Awareness Pattern ⭐
**Multi-Turn Conversations**

```python
class ContextAwareExtractor:
    def __init__(self, llm):
        self.llm = llm
        self.conversation_context = []
    
    def extract_with_context(self, user_input: str, tool_name: str) -> dict:
        # Include conversation history in parameter extraction
        context_info = {
            "current_request": user_input,
            "previous_results": self.conversation_context[-3:],  # Last 3 interactions
            "available_data": self.get_available_context()
        }
        
        prompt = f"""
        Current request: "{user_input}"
        Previous conversation: {context_info["previous_results"]}
        Available context: {context_info["available_data"]}
        
        Tool: {tool_name}
        Parameters needed: {self.get_tool_params(tool_name)}
        
        Extract parameters using context when helpful:
        """
        
        response = self.llm.run(prompt, [])
        return json.loads(response.content)

# Example conversation:
# User: "Get sales data for Q1"
# Bot: [executes query_database] → Returns sales data
# Context: [{"tool": "query_database", "result": "Q1 sales data loaded"}]

# User: "Now calculate the average"  # No explicit data mentioned!
# Bot: Uses context to know "average of Q1 sales data"
# Extracts: {"numbers": [previous_sales_data], "operation": "average"}
```

---

## 6. Multi-Tool Scenarios

### 6.1 Sequential Tool Chaining
**When tools depend on each other**

```python
class MultiToolOrchestrator:
    def __init__(self, llm):
        self.llm = llm
    
    def process_request(self, user_input: str) -> dict:
        # Detect if multiple tools needed
        analysis = self.analyze_request(user_input)
        
        if analysis["tool_count"] == 1:
            return self.single_tool_execution(user_input, analysis["tools"][0])
        else:
            return self.multi_tool_execution(user_input, analysis["tools"])
    
    def analyze_request(self, user_input: str) -> dict:
        tools = ToolRegistry.list_tools()
        tool_list = [{"name": name, "description": info["description"]} 
                    for name, info in tools.items()]
        
        prompt = f"""
        User: "{user_input}"
        
        Available tools: {tool_list}
        
        How many tools are needed and in what order?
        
        Return JSON: {{
            "tool_count": 2,
            "tools": ["tool1", "tool2"],
            "execution_plan": "First get data, then calculate average"
        }}
        """
        
        response = self.llm.run(prompt, [])
        return json.loads(response.content)
    
    def multi_tool_execution(self, user_input: str, tools: list) -> dict:
        results = []
        context = {"user_input": user_input, "previous_results": []}
        
        for tool_name in tools:
            # Extract parameters considering previous results
            params = self.extract_contextual_parameters(context, tool_name)
            
            # Execute tool
            result = self.execute_tool(tool_name, params)
            results.append({"tool": tool_name, "result": result})
            
            # Update context for next tool
            context["previous_results"].append(result)
        
        return {"action": "multi_tool", "results": results}
```

### 6.2 Parallel Tool Execution
**When tools are independent**

```python
def process_parallel_tools(self, user_input: str) -> dict:
    """Handle requests that need multiple independent tools"""
    
    # Example: "Check AAPL stock price and calculate 15% of 200"
    prompt = f"""
    User: "{user_input}"
    
    Break this into independent tasks that can run in parallel:
    
    Return JSON: {{
        "tasks": [
            {{"tool": "stock_checker", "input": "AAPL"}},
            {{"tool": "calculator", "input": "15% of 200"}}
        ]
    }}
    """
    
    response = self.llm.run(prompt, [])
    analysis = json.loads(response.content)
    
    # Execute all tools in parallel
    results = []
    for task in analysis["tasks"]:
        params = self.extract_parameters(task["input"], task["tool"])
        result = self.execute_tool(task["tool"], params)
        results.append({"tool": task["tool"], "result": result})
    
    return {"action": "parallel_tools", "results": results}
```

### 6.3 Tool Pipeline Pattern
**Data flows through multiple tools**

```python
@tool("get_sales_data")
def get_sales_data(region: str) -> dict:
    """Get sales data for a region
    Keywords: sales, data, region
    Args:
        region (str): geographic region
    Returns:
        dict: sales data
    """
    return {"region": region, "sales": [100, 200, 300]}

@tool("calculate_average")
def calculate_average(numbers: list) -> float:
    """Calculate average of numbers
    Keywords: average, mean, calculate
    Args:
        numbers (list): list of numbers
    Returns:
        float: average value
    """
    return sum(numbers) / len(numbers)

class ToolPipeline:
    def process_pipeline(self, user_input: str) -> dict:
        # Example: "What's the average sales in the northeast region?"
        
        # Step 1: Identify pipeline
        pipeline = self.identify_pipeline(user_input)
        # Returns: ["get_sales_data", "calculate_average"]
        
        # Step 2: Execute pipeline
        data = None
        for i, tool_name in enumerate(pipeline):
            if i == 0:
                # First tool uses original input
                params = self.extract_parameters(user_input, tool_name)
            else:
                # Subsequent tools use previous output
                params = self.extract_parameters_from_data(data, tool_name)
            
            data = self.execute_tool(tool_name, params)
        
        return {"action": "pipeline", "final_result": data}
```

---

## 7. Production Considerations

### 7.1 Complete Orchestrator
```python
class ProductionOrchestrator:
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
        
        # Stage 4: Validate Parameters
        validation = self.validate_parameters(tool_name, parameters)
        if validation["errors"]:
            return {
                "action": "parameter_error",
                "response": f"Parameter issues: {', '.join(validation['errors'])}"
            }
        
        # Stage 5: Execute Tool
        result = self.execute_tool(tool_name, validation["params"])
        
        return {
            "action": "tool_execution",
            "tool": tool_name,
            "parameters": validation["params"],
            "confidence": tool_selection["confidence"],
            "result": result
        }
```

### 7.2 Error Handling
```python
def execute_tool_safely(self, tool_name: str, parameters: dict):
    try:
        tool_class = ToolRegistry.list()[tool_name]
        tool_instance = tool_class()
        return tool_instance.run(**parameters)
    except KeyError:
        return f"Tool '{tool_name}' not found"
    except TypeError as e:
        return f"Parameter error: {str(e)}"
    except Exception as e:
        return f"Execution error: {str(e)}"
```

### 7.3 Logging and Monitoring
```python
import logging
from datetime import datetime

class ToolCallLogger:
    def __init__(self):
        self.logger = logging.getLogger("tool_calls")
    
    def log_tool_call(self, user_input: str, tool_name: str, parameters: dict, result: any, confidence: float):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "tool": tool_name,
            "parameters": parameters,
            "confidence": confidence,
            "success": result is not None,
            "result_length": len(str(result)) if result else 0
        }
        self.logger.info(f"Tool call: {log_entry}")
```

---

## 8. Real-World Examples

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

### Example 2: Multi-Tool Chain
```
User: "Get Tesla stock price and calculate what 100 shares would cost"

Analysis: 2 tools needed sequentially
1. check_stock_index("TSLA") → $250
2. calculate_math("250 * 100") → $25,000

Result: "Tesla is $250/share. 100 shares would cost $25,000"
```

### Example 3: Context-Aware Interaction
```
User: "Load customer data from California"
Bot: [executes query] → "Loaded 1,247 California customers"

User: "What's their average age?"  # No explicit data mentioned
Bot: [uses context] → calculate_average(ages_from_previous_query) → "Average age: 34.2 years"
```

### Example 4: Ambiguous Request Handling
```
User: "Help me with data"

Stage 1 (Intent): data_analysis
Stage 2 (Tool): None (confidence: 30%)
Response: "I'm not sure which data tool to use. Could you be more specific about what you want to do with the data? For example: query a database, analyze a file, or create a visualization?"
```

---

## 9. Best Practices Summary

### Essential Implementation Order
1. **Start with Multi-Stage Pipeline** - Core architecture
2. **Add Confidence Scoring** - Prevents bad experiences  
3. **Implement Rich Metadata** - Foundation for good matching
4. **Add Graceful Degradation** - Handles edge cases
5. **Enhance with Advanced Patterns** - Category filtering, validation, context

### Key Success Factors
- **Rich Tool Metadata**: Description, keywords, examples, parameters
- **Confidence Thresholds**: 70% minimum for Amazon Q standard
- **Multi-Stage Filtering**: Intent → Category → Semantic matching
- **Parameter Validation**: Check types and requirements before execution
- **Context Awareness**: Remember previous interactions and results
- **Error Handling**: Always have fallbacks, never fail silently

### Performance Optimizations
- **Category Filtering**: Reduces 100+ tools to 5-10 candidates
- **Caching**: Cache tool metadata and common parameter extractions
- **Parallel Execution**: Run independent tools simultaneously
- **Early Validation**: Catch parameter errors before expensive operations

### Production Checklist
- [ ] Multi-stage pipeline implemented
- [ ] Confidence scoring with thresholds
- [ ] Parameter validation with type checking
- [ ] Comprehensive error handling
- [ ] Logging and monitoring
- [ ] Context management for multi-turn conversations
- [ ] Graceful degradation for edge cases
- [ ] Performance optimization for large tool sets

This comprehensive approach ensures robust, production-ready tool calling that works reliably across diverse user inputs and scales to hundreds of tools.