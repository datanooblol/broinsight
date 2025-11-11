from broinsight.statemachines.utils import get_state_str, get_return_values_ast
from pathlib import Path
from typing import Optional, Literal, Protocol
from .utils import to_mermaid_with_conditions

class StateGroupProtocol(Protocol):
    """Protocol for state group interface"""
    def get(self, state_name): ...
    def state_graph(self): ...

class StateGroup:
    def __init__(self, name: str = "default"):
        self.name = name
        self._states = {}
    
    def register(self, state_name):
        """Instance-based decorator like FastAPI's @app.route"""
        def decorator(cls):
            state_name_str = get_state_str(state_name)
            if state_name_str not in self._states:
                self._states[state_name_str] = cls
            else:
                print(f"Already registered in {self.name}: {state_name_str}")
            return cls
        return decorator
    
    def get(self, state_name):
        return self._states[get_state_str(state_name)]()
    
    def state_graph(self):
        transitions = {}
        for k, v in self._states.items():
            returns = get_return_values_ast(v.next_state)
            transitions[k] = returns
        return transitions
    
    def create_machine(self, start_state, end_state):
        return GroupStateMachine(self, start_state, end_state)

class GroupStateMachine:
    def __init__(self, state_group: StateGroupProtocol, start_state, end_state):
        self.state_group = state_group
        self.start_state = start_state
        self.end_state = get_state_str(end_state)
    
    def run(self, context):
        current_state = get_state_str(self.start_state)
        
        while current_state != self.end_state:
            state_instance = self.state_group.get(current_state)
            next_state = state_instance.run(context)
            next_state = get_state_str(next_state)
            context.execution_trace.append({
                "current_state": current_state,
                "next_state": next_state
            })
            current_state = next_state
            
        return context
    
class CompositeStateGroup:
    def __init__(self, name: str, *state_groups: StateGroup):
        self.name = name
        self._states = {}
        
        # Merge all state groups
        for group in state_groups:
            for state_name, state_class in group._states.items():
                if state_name in self._states:
                    print(f"Warning: State '{state_name}' from {group.name} overrides existing state")
                self._states[state_name] = state_class
    
    def get(self, state_name):
        return self._states[get_state_str(state_name)]()
    
    def state_graph(self):
        transitions = {}
        for k, v in self._states.items():
            returns = get_return_values_ast(v.next_state)
            transitions[k] = returns
        return transitions

    def to_mermaid(self, save_path: Optional[str] = None, direction: Literal["LR", "TB"] = "TB"):
        transitions = self.state_graph()
        mermaid_str = to_mermaid_with_conditions(transitions, direction)
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("```mermaid\n{mermaid_str}\n```".format(mermaid_str=mermaid_str))
        return mermaid_str


    def create_machine(self, start_state, end_state):
        return GroupStateMachine(self, start_state, end_state)

