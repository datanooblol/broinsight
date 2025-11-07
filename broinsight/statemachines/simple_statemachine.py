from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from .utils import get_return_values_ast, to_mermaid_with_conditions, get_state_str
from enum import Enum
from pathlib import Path

class BaseSimpleContext(BaseModel):
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)

class BaseSimpleState(ABC):
    @abstractmethod
    def next_state(self, *args, **kwargs)->Enum | str: pass
    @abstractmethod
    def run(self, context)->None|Any: pass

class SimpleStateRegistry:
    _states = {}

    @classmethod
    def register(cls, state_name, state_class):
        state_name_str = get_state_str(state_name)
        if state_name_str not in cls._states:
            cls._states[state_name_str] = state_class
        else:
            print(f"Already registered: {state_name_str}")

    @classmethod
    def get(cls, state_name:Any)->BaseSimpleState:
        return cls._states[get_state_str(state_name)]()

    @classmethod
    def state_graph(cls):
        transitions = {}
        for k, v in cls._states.items():
            returns = get_return_values_ast(v.next_state)
            transitions[k] = returns
        return transitions
    
    @classmethod
    def to_mermaid(cls, save_path:Optional[str]=None, direction:Literal["LR", "TB"]="TB"):
        transitions = cls.state_graph()
        mermaid_str = to_mermaid_with_conditions(transitions, direction)
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories
            path.write_text("```mermaid\n{mermaid_str}\n```".format(mermaid_str=mermaid_str))
        return mermaid_str

    @classmethod
    def clear_all_states(cls):
        cls._states = {}
    
def simple_state(state_name):
    def decorator(cls):
        SimpleStateRegistry.register(state_name, cls)
        return cls
    return decorator

class SimpleStateMachine:
    def __init__(self, start_state, end_state):
        self.start_state = start_state
        self.end_state = get_state_str(end_state)
    
    def run(self, context):
        current_state = self.start_state
        current_state = get_state_str(current_state)

        while current_state != self.end_state:
            state_instance = SimpleStateRegistry.get(current_state)
            next_state = state_instance.run(context)
            next_state = get_state_str(next_state)
            context.execution_trace.append({
                "state": current_state,
                "next_state": next_state
            })
            current_state = next_state
            
        return context