# Tool System with Parameter Validation

## Overview

BroInsight's tool system provides automatic function registration, parameter extraction from LLM responses, and robust type validation using Python's `inspect` module.

## Tool Registration

### Basic Tool Definition

```python
from broinsight.tools.register import tool, ToolBox
from datetime import datetime

@tool()
def add_calendar(event_name: str, datetime: datetime) -> str:
    """Add event into calendar
    Args:
        event_name (str) : name of the event
        datetime (datetime) : a datetime of the event
    Returns:
        str : successfully added message
    """
    return f"{event_name} at {datetime}"

@tool()
def check_stock_index(index: str) -> str:
    """Check a stock by index from Yahoo API
    Keywords: stock, investment, finance
    Args:
        index (str) : a stock index
    Returns:
        str : a response from Yahoo API
    """
    return f"Stock data for {index}"
```

### Automatic Metadata Extraction

The `@tool()` decorator automatically extracts:
- **Function signature** with parameter types
- **Description** from docstring first line
- **Parameters** with types and descriptions from Args section
- **Return type** from Returns section
- **Keywords** for categorization

## Complete Tool Calling Flow

### 1. Get Tool Information

```python
# Retrieve tool metadata
tool_call = ToolBox.get_tool_info("add_calendar")
name = tool_call['name']
function = tool_call['function']
description = tool_call['description']
parameters = tool_call["parameters"]
signature = tool_call["signature"]  # inspect.Signature object

# Format for LLM prompt
tool_prompt = f"""
Tool: {name}
Description: {description}
Parameters: {parameters}
""".strip()
```

### 2. LLM Parameter Extraction

```python
from broinsight.core.llm import LocalOpenAI, UserMessage
from broinsight.utils.parse_string import parse_json

system_prompt = """
- Extract input parameters from USER_INPUT based on provided TOOLS
- Return in JSON codeblock that matches the TOOLS
- Return only the JSON codeblock
```json
{"parameters": {"key": value, "key": value}}
```
""".strip()

model = LocalOpenAI()
user_input = "I wanna see grandma on 10 October 2025 at noon."
content = f"TOOLS:\n\n{tool_prompt}\n\nUSER_INPUT:\n\n{user_input}\n\n"
response = model.run(system_prompt, messages=[UserMessage(content=content)])

# Parse LLM response
import json
params = json.loads(parse_json(response.content))
print(params)
# Output: {'parameters': {'event_name': 'see grandma', 'datetime': '2025-10-10T12:00:00'}}
```

### 3. Parameter Validation with inspect.Signature

```python
from broinsight.tools.register import TypeValidator

# Bind parameters to function signature
signature = tool_call["signature"]
bound_args = signature.bind(**params["parameters"])
bound_args.apply_defaults()  # Fill in any default values

# Validate and convert types
validator = TypeValidator()
validated_params = validator.validate_types(bound_args, signature)

print(validated_params)
# Output: {'event_name': 'see grandma', 'datetime': datetime.datetime(2025, 10, 10, 12, 0)}
```

### 4. Safe Function Execution

```python
# Execute with validated parameters
result = function(**validated_params)
print(result)
# Output: "see grandma at 2025-10-10 12:00:00"
```

## Type Validation System

### TypeValidator Class

```python
class TypeValidator:
    def __init__(self):
        self.converters = {
            datetime: self.convert_datetime,
            int: self.convert_int,
            float: self.convert_float,
            str: self.convert_str,
        }
    
    def convert_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value)
    
    def convert_int(self, value: str) -> int:
        return int(value)
    
    def convert_float(self, value: str) -> float:
        return float(value)
    
    def convert_str(self, value) -> str:
        return str(value)
    
    def validate_types(self, bound_args, signature):
        for name, value in bound_args.arguments.items():
            expected_type = signature.parameters[name].annotation
            if expected_type != inspect.Parameter.empty:
                if not isinstance(value, expected_type):
                    try:
                        converted_value = self.convert_value(value, expected_type)
                        bound_args.arguments[name] = converted_value
                    except (ValueError, TypeError):
                        raise TypeError(f"{name}: cannot convert {type(value)} to {expected_type}")
        
        return bound_args.arguments
```

### Supported Type Conversions

- **String to datetime**: `'2025-10-10T12:00:00'` → `datetime(2025, 10, 10, 12, 0)`
- **String to int**: `'42'` → `42`
- **String to float**: `'19.99'` → `19.99`
- **Any to string**: `123` → `'123'`

## Error Handling

### Parameter Validation Errors

```python
try:
    bound_args = signature.bind(**params["parameters"])
    validated_params = validator.validate_types(bound_args, signature)
except TypeError as e:
    print(f"Parameter validation failed: {e}")
    # Handle missing required parameters, wrong types, etc.
```

### Common Error Scenarios

1. **Missing required parameter**
   ```python
   # Error: missing a required argument: 'event_name'
   ```

2. **Wrong parameter name**
   ```python
   # Error: got an unexpected keyword argument 'wrong_name'
   ```

3. **Type conversion failure**
   ```python
   # Error: datetime: cannot convert <class 'int'> to <class 'datetime.datetime'>
   ```

## Benefits

### 1. **Automatic Validation**
- Parameter names and counts checked by `signature.bind()`
- Type annotations enforced with automatic conversion
- Default values handled seamlessly

### 2. **Robust Type Conversion**
- Handles common LLM response format mismatches
- Extensible converter system for custom types
- Graceful error handling with clear messages

### 3. **Developer Experience**
- Simple `@tool()` decorator registration
- Automatic docstring parsing for metadata
- Clean separation between tool logic and validation

### 4. **Production Ready**
- Prevents runtime errors from malformed LLM responses
- Comprehensive error messages for debugging
- Type-safe function execution

## Example: Complete Tool Call

```python
# 1. Register tool
@tool()
def add_calendar(event_name: str, datetime: datetime) -> str:
    """Add event into calendar
    Args:
        event_name (str) : name of the event
        datetime (datetime) : a datetime of the event
    Returns:
        str : successfully added message
    """
    return f"{event_name} at {datetime}"

# 2. Get tool info and prompt LLM
tool_call = ToolBox.get_tool_info("add_calendar")
# ... LLM processing ...

# 3. Validate and execute
signature = tool_call["signature"]
bound_args = signature.bind(**llm_params)
bound_args.apply_defaults()

validator = TypeValidator()
validated_params = validator.validate_types(bound_args, signature)

result = tool_call['function'](**validated_params)
```

This system ensures that LLM-generated parameters are properly validated and converted before function execution, providing a robust foundation for tool-based AI applications.