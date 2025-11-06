import ast
import inspect
import textwrap
from typing import Literal
from enum import Enum

def get_return_values_ast(method):
    source = inspect.getsource(method)
    # Fix indentation issues
    source = textwrap.dedent(source)
    tree = ast.parse(source)
    
    returns = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Attribute):  # SimpleState.CHAT
                returns.append(node.value.attr)
            elif isinstance(node.value, ast.Constant):  # "string"
                returns.append(node.value.value)
    
    return returns

def to_mermaid_with_conditions(transitions, direction:Literal["LR", "TB"]="LR"):
    """Use labels to show conditional vs direct transitions"""
    lines = [f"flowchart {direction}"]
    
    for from_state, to_states in transitions.items():
        if len(to_states) == 1:
            # Single transition - no label
            lines.append(f"    {from_state} --> {to_states[0]}")
        else:
            # Multiple transitions - add condition labels
            for i, to_state in enumerate(to_states):
                lines.append(f"    {from_state} -.-> {to_state}")
    
    return "\n".join(lines)

def get_state_str(state):
    return state.value.upper() if isinstance(state, Enum) else state.upper()