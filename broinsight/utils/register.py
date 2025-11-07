class AgentRegistry:
    _agents = {}

    @classmethod
    def register(cls, name:str, agent_class):
        cls._agents[name] = agent_class
        return agent_class
    
    @classmethod
    def list(cls):
        return cls._agents
    
def agent(name):
    def decorator(cls):
        AgentRegistry.register(name, cls)
        return cls
    return decorator

# class ToolBox:
#     _tools = {}

#     @classmethod
#     def register(cls, name:str, func_tool):
#         cls._tools[name] = func_tool
#         return func_tool
    
#     @classmethod
#     def list(cls):
#         return cls._tools
    
# def tool(name):
#     def decorator(func_tool):
#         ToolBox.register(name, func_tool)
#         return func_tool
#     return decorator

import inspect
import re
from typing import Dict, List, Optional

def parse_google_docstring(func) -> Dict:
    """Parse Google-style docstring to extract tool metadata"""
    docstring = inspect.getdoc(func)
    if not docstring:
        return {}
    
    # Extract description (first line)
    lines = docstring.strip().split('\n')
    description = lines[0].strip()
    
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
    
def tool(name:Optional[str] = None):
    def decorator(func):
        # Parse docstring automatically
        metadata = parse_google_docstring(func)
        
        # Register with parsed metadata
        ToolBox.register(name or func.__name__, func, metadata)
        return func
    return decorator