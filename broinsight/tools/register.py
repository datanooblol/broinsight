import inspect
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

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
                # Parse: param_name (type) : description
                match = re.match(r'(\w+)\s*\(([^)]+)\)\s*:\s*(.+)', line)
                if match:
                    param_name, param_type, param_desc = match.groups()
                    parameters[param_name] = f"{param_type} - {param_desc}"
    
    # Extract return type
    returns_match = re.search(r'Returns:\s*\n\s*(\w+)\s*:\s*(.+)', docstring)
    return_type = None
    if returns_match:
        return_type = f"{returns_match.group(1)} - {returns_match.group(2)}"
    
    return {
        "description": description,
        "category": category,
        "keywords": keywords,
        "parameters": parameters,
        "returns": return_type
    }

class ToolBox:
    _tools = {}
    
    @classmethod
    def register(cls, name: str, func, metadata: dict):
        cls._tools[name] = {
            "function": func,
            "name": name,
            "description": metadata.get("description", ""),
            "category": metadata.get("category", "general"),
            "keywords": metadata.get("keywords", []),
            "parameters": metadata.get("parameters", {}),
            "returns": metadata.get("returns", ""),
            "signature": inspect.signature(func)
        }
    
    @classmethod
    def get_tool_info(cls, name: str):
        return cls._tools.get(name, {})
    
    @classmethod
    def list_tools(cls):
        return {name: info for name, info in cls._tools.items()}

    @classmethod
    def list_tool_metadata(cls):
        tools = [
            f"{t['name']} {t['description']} {t['category']} {t['keywords']}" 
            for _, t in cls.list_tools().items()
        ]
        return tools

    @classmethod
    def get_tools(cls, names:List[str]):
        tools = []
        for name in names:
            tool = cls._tools.get(name)
            if tool:
                tools.append(tool)
        return tools
    
    @classmethod
    def prompt(cls, names:Optional[List[str]]=None):
        if names is None:
            names = list(cls._tools.keys())
        _prompt = []
        for enum, name in enumerate(names):
            t = cls._tools.get(name, {})
            p = f"- {t['name']}: {t['description']} (parameters: {list(t['parameters'].keys())})"
            _prompt.append(p)
        return _prompt

    @classmethod
    def tool_prompt(cls, name:str):
        tool_call = ToolBox.get_tool_info(name)
        name = tool_call['name']
        function = tool_call['function']
        description = tool_call['description']
        parameters = tool_call["parameters"]
        tp = [
            f"Tool: {name}",
            f"Description: {description}",
            f"Parameters: {parameters}",
        ]
        return tp
    
def tool(name:Optional[str] = None):
    def decorator(func):
        # Parse docstring automatically
        metadata = parse_google_docstring(func)
        
        # Register with parsed metadata
        ToolBox.register(name or func.__name__, func, metadata)
        return func
    return decorator

class TypeConverter:
    @staticmethod
    def convert_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value)
    
    @staticmethod
    def convert_int(value: str) -> int:
        return int(value)
    
    @staticmethod
    def convert_float(value: str) -> float:
        return float(value)
    
    @staticmethod
    def convert_str(value) -> str:
        return str(value)

class TypeValidator:
    def __init__(self):
        self.converters = {
            datetime: TypeConverter.convert_datetime,
            int: TypeConverter.convert_int,
            float: TypeConverter.convert_float,
            str: TypeConverter.convert_str,
        }
    
    def convert_value(self, value, expected_type):
        if expected_type in self.converters:
            return self.converters[expected_type](value)
        else:
            # Fallback to default constructor
            return expected_type(value)
    
    def validate_types(self, bound_args: inspect.BoundArguments, signature: inspect.Signature):
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

# Usage
# validator = TypeValidator()
# validator.validate_types(bound_args, signature)
