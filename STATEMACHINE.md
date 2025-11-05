# State Machine Pattern Documentation

## Overview

A **State Machine** is a computational model that manages workflow execution through discrete states and transitions. This pattern provides predictable, maintainable, and testable workflow management for complex business logic.

## Core Components

### 1. **State (Enum)** - The Blueprint
**Purpose**: Defines all possible states in your workflow
```python
class State(Enum):
    ROUTER = "router"
    PROCESS = "process"
    COMPLETE = "complete"
```
**Benefits**:
- Clear overview of entire workflow
- Type safety and IDE autocomplete
- Prevents invalid state transitions
- Serves as living documentation

### 2. **DataContext (Pydantic BaseModel)** - The Data Specification
**Purpose**: Defines the data structure that flows through all states
```python
class DataContext(BaseModel):
    user_input: str
    result: Optional[str] = Field(default=None)
    execution_trace: List[str] = Field(default_factory=list)
```
**Benefits**:
- Type validation and serialization
- Clear data contract between states
- IDE support with field autocomplete
- Built-in documentation through field types

### 3. **BaseState (ABC)** - The Contract
**Purpose**: Enforces consistent interface for all state implementations
```python
class BaseState(ABC):
    @abstractmethod
    def execute(self, context: DataContext) -> State:
        pass
```
**Benefits**:
- Guarantees all states implement required methods
- Consistent interface across all states
- Easy to mock for testing
- Clear separation of concerns

### 4. **StateMachine** - The Engine
**Purpose**: Orchestrates state execution and transitions
```python
class StateMachine:
    def run(self, **initial_data) -> DataContext:
        # Iteratively execute states until completion
```
**Benefits**:
- Centralized execution control
- Built-in execution tracing
- Error handling at transition level
- Predictable execution flow

## Complete Implementation

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from abc import ABC, abstractmethod

# 1. BLUEPRINT: Define all possible states
class State(Enum):
    ROUTER = "router"
    CHAT = "chat"
    SQL = "sql"
    COMPLETE = "complete"

# 2. DATA SPEC: Define data flowing through workflow
class DataContext(BaseModel):
    user_input: str
    answer: Optional[str] = Field(default=None)
    route_type: Optional[str] = Field(default=None)
    sql_query: Optional[str] = Field(default=None)
    execution_trace: List[str] = Field(default_factory=list)

# 3. CONTRACT: Enforce consistent state interface
class BaseState(ABC):
    @abstractmethod
    def execute(self, context: DataContext) -> State:
        pass

# 4. REGISTRY: Manage state registration and retrieval
class StateRegistry:
    _states = {}
    
    @classmethod
    def register(cls, state_enum_value: State, state_class):
        cls._states[state_enum_value] = state_class
    
    @classmethod
    def get(cls, state_enum_value: State):
        return cls._states[state_enum_value]()

def state(state_enum_value: State):
    def decorator(cls):
        StateRegistry.register(state_enum_value, cls)
        return cls
    return decorator

# 5. ENGINE: Orchestrate state execution
class StateMachine:
    def __init__(self, start_state: State, complete_state: State, context_class):
        self.start_state = start_state
        self.complete_state = complete_state
        self.context_class = context_class
    
    def run(self, **initial_data) -> DataContext:
        context = self.context_class(**initial_data)
        current_state = self.start_state
        
        while current_state != self.complete_state:
            context.execution_trace.append(current_state.value)
            state_instance = StateRegistry.get(current_state)
            current_state = state_instance.execute(context)
        
        return context
```

## Usage Example

```python
# Define workflow states
@state(State.ROUTER)
class Router(BaseState):
    def execute(self, context: DataContext) -> State:
        if "sql" in context.user_input.lower():
            context.route_type = "sql"
            return State.SQL
        else:
            context.route_type = "chat"
            return State.CHAT

@state(State.SQL)
class SQLProcessor(BaseState):
    def execute(self, context: DataContext) -> State:
        context.sql_query = f"SELECT * FROM data WHERE query LIKE '%{context.user_input}%'"
        return State.CHAT

@state(State.CHAT)
class ChatHandler(BaseState):
    def execute(self, context: DataContext) -> State:
        if context.route_type == "sql":
            context.answer = f"SQL: {context.sql_query} | Results found"
        else:
            context.answer = f"Chat: {context.user_input}"
        return State.COMPLETE

# Execute workflow
machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
result = machine.run(user_input="show me data")
print(result.answer)  # "SQL: SELECT * FROM data WHERE query LIKE '%show me data%' | Results found"
print(result.execution_trace)  # ['router', 'sql', 'chat']
```

## Testing Strategies

### 1. **Individual State Testing**
Test each state in isolation with controlled inputs:

```python
import pytest

def test_router_sql_detection():
    """Test router correctly identifies SQL requests"""
    context = DataContext(user_input="show me sql data")
    router = Router()
    
    next_state = router.execute(context)
    
    assert next_state == State.SQL
    assert context.route_type == "sql"

def test_router_chat_detection():
    """Test router correctly identifies chat requests"""
    context = DataContext(user_input="hello world")
    router = Router()
    
    next_state = router.execute(context)
    
    assert next_state == State.CHAT
    assert context.route_type == "chat"

def test_sql_processor():
    """Test SQL processor generates correct query"""
    context = DataContext(user_input="sales data", route_type="sql")
    sql_processor = SQLProcessor()
    
    next_state = sql_processor.execute(context)
    
    assert next_state == State.CHAT
    assert "SELECT * FROM data" in context.sql_query
    assert "sales data" in context.sql_query

def test_chat_handler_sql_response():
    """Test chat handler formats SQL responses correctly"""
    context = DataContext(
        user_input="sales data",
        route_type="sql",
        sql_query="SELECT * FROM sales"
    )
    chat_handler = ChatHandler()
    
    next_state = chat_handler.execute(context)
    
    assert next_state == State.COMPLETE
    assert "SQL:" in context.answer
    assert "SELECT * FROM sales" in context.answer

def test_chat_handler_regular_response():
    """Test chat handler formats regular responses correctly"""
    context = DataContext(user_input="hello", route_type="chat")
    chat_handler = ChatHandler()
    
    next_state = chat_handler.execute(context)
    
    assert next_state == State.COMPLETE
    assert context.answer == "Chat: hello"
```

### 2. **Full Workflow Testing**
Test complete end-to-end execution:

```python
def test_sql_workflow_complete():
    """Test complete SQL workflow execution"""
    machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
    
    result = machine.run(user_input="show me sales data")
    
    assert result.route_type == "sql"
    assert result.sql_query is not None
    assert "SQL:" in result.answer
    assert result.execution_trace == ['router', 'sql', 'chat']

def test_chat_workflow_complete():
    """Test complete chat workflow execution"""
    machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
    
    result = machine.run(user_input="hello world")
    
    assert result.route_type == "chat"
    assert result.sql_query is None
    assert result.answer == "Chat: hello world"
    assert result.execution_trace == ['router', 'chat']

def test_workflow_with_invalid_input():
    """Test workflow handles edge cases gracefully"""
    machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
    
    result = machine.run(user_input="")
    
    assert result.answer is not None
    assert len(result.execution_trace) > 0
```

### 3. **Mock Testing**
Replace expensive operations with mocks:

```python
class MockSQLProcessor(BaseState):
    """Mock SQL processor for testing without database"""
    def execute(self, context: DataContext) -> State:
        context.sql_query = "MOCK_QUERY"
        return State.CHAT

def test_with_mock_sql():
    """Test workflow with mocked SQL processor"""
    # Replace real SQL processor with mock
    StateRegistry.register(State.SQL, MockSQLProcessor)
    
    machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
    result = machine.run(user_input="sql query")
    
    assert result.sql_query == "MOCK_QUERY"
    
    # Restore original (cleanup)
    StateRegistry.register(State.SQL, SQLProcessor)
```

### 4. **Error Handling Testing**
Test failure scenarios and recovery:

```python
class FailingSQLProcessor(BaseState):
    """SQL processor that simulates failure"""
    def execute(self, context: DataContext) -> State:
        raise Exception("Database connection failed")

def test_error_handling():
    """Test workflow handles state failures gracefully"""
    StateRegistry.register(State.SQL, FailingSQLProcessor)
    
    machine = StateMachine(State.ROUTER, State.COMPLETE, DataContext)
    
    with pytest.raises(Exception, match="Database connection failed"):
        machine.run(user_input="sql query")
```

## Advanced Patterns

### Namespaced Registries
For multiple independent workflows:

```python
class StateRegistry:
    _registries = {}
    
    @classmethod
    def register(cls, registry_name: str, state_enum_value: State, state_class):
        if registry_name not in cls._registries:
            cls._registries[registry_name] = {}
        cls._registries[registry_name][state_enum_value] = state_class

def state(registry_name: str, state_enum_value: State):
    def decorator(cls):
        StateRegistry.register(registry_name, state_enum_value, cls)
        return cls
    return decorator

# Usage:
@state("workflow_a", State.ROUTER)
class WorkflowARouter(BaseState): pass

@state("workflow_b", State.ROUTER)  
class WorkflowBRouter(BaseState): pass
```

## Best Practices

### 1. **State Design**
- Keep states focused on single responsibility
- Use descriptive state names
- Minimize state-to-state dependencies

### 2. **Context Design**
- Include all data needed by any state
- Use Optional fields for state-specific data
- Add execution_trace for debugging

### 3. **Testing Strategy**
- Test individual states first
- Test complete workflows second
- Use mocks for expensive operations
- Test error scenarios

### 4. **Debugging**
- Always include execution_trace
- Log state transitions
- Use descriptive error messages
- Validate context at state boundaries

## When to Use State Machines

**✅ Good for:**
- Complex business workflows
- Multi-step processes with branching
- Systems requiring audit trails
- Workflows with error recovery
- Processes with conditional routing

**❌ Not ideal for:**
- Simple linear processes
- Real-time systems with strict latency requirements
- Highly parallel/concurrent workflows
- Simple CRUD operations

## Adaptation Guide

To adapt this pattern to your use case:

1. **Define your States**: List all steps in your workflow
2. **Design your Context**: Include all data fields needed
3. **Implement BaseState**: Create your state interface
4. **Build State Classes**: Implement each workflow step
5. **Test Incrementally**: Start with individual states, then full workflow

This pattern scales from simple 3-state workflows to complex multi-branch processes with dozens of states, making it perfect for evolving business requirements.

## Integrating Multiple State Machines

For complex systems, you often need to combine multiple state machines. Here are the main integration patterns:

### 1. **Hierarchical State Machines (Sub-Workflows)**
Delegate to complete sub-workflows from within states:

```python
class State(Enum):
    ROUTER = "router"
    CHAT_WORKFLOW = "chat_workflow"  # Delegates to chat machine
    SQL_WORKFLOW = "sql_workflow"    # Delegates to sql machine
    COMPLETE = "complete"

@state("main_workflow", State.CHAT_WORKFLOW)
class ChatWorkflowDelegate(BaseState):
    def execute(self, context: DataContext) -> State:
        # Run entire chat workflow as sub-process
        chat_machine = StateMachine("chat_workflow", State.ROUTER, State.COMPLETE, DataContext)
        result = chat_machine.run(**context.dict())
        
        # Merge results back
        context.answer = result.answer
        context.execution_trace.extend(["sub_chat"] + result.execution_trace)
        
        return State.COMPLETE
```

**Benefits**: Clean separation, reusable sub-workflows, clear hierarchy
**Use Case**: Complex workflows with distinct phases

### 2. **Pipeline State Machines (Sequential)**
Chain multiple workflows where output of one becomes input of next:

```python
class PipelineStateMachine:
    def __init__(self, machines: List[StateMachine]):
        self.machines = machines
    
    def run(self, **initial_data) -> DataContext:
        context = DataContext(**initial_data)
        
        for machine in self.machines:
            # Each machine processes the context from previous machine
            result = machine.run(**context.dict())
            context = result  # Pass result to next machine
        
        return context

# Usage: Process through multiple workflows sequentially
preprocessing_machine = StateMachine("preprocessing", State.CLEAN, State.COMPLETE, DataContext)
analysis_machine = StateMachine("analysis", State.ANALYZE, State.COMPLETE, DataContext)
reporting_machine = StateMachine("reporting", State.REPORT, State.COMPLETE, DataContext)

pipeline = PipelineStateMachine([preprocessing_machine, analysis_machine, reporting_machine])
result = pipeline.run(user_input="raw data")
```

**Benefits**: Linear processing, data transformation pipeline, easy to debug
**Use Case**: ETL processes, data analysis pipelines

### 3. **Conditional Workflow Orchestrator**
Dynamically route to different workflows based on conditions:

```python
class WorkflowOrchestrator:
    def __init__(self):
        self.workflows = {}
    
    def register_workflow(self, name: str, machine: StateMachine):
        self.workflows[name] = machine
    
    def run_conditional(self, condition_func, **initial_data) -> DataContext:
        """Run workflow based on condition function"""
        workflow_name = condition_func(initial_data)
        return self.workflows[workflow_name].run(**initial_data)

# Setup orchestrator
orchestrator = WorkflowOrchestrator()
orchestrator.register_workflow("chat", chat_machine)
orchestrator.register_workflow("sql", sql_machine)

# Conditional routing
def route_workflow(data):
    if "sql" in data.get("user_input", "").lower():
        return "sql"
    return "chat"

result = orchestrator.run_conditional(route_workflow, user_input="show me data")
```

**Benefits**: Dynamic routing, easy to add new workflows, centralized management
**Use Case**: Multi-tenant systems, feature flags, A/B testing

### 4. **Parallel State Machines (Concurrent)**
Run multiple workflows simultaneously and combine results:

```python
import asyncio
from typing import List

class ParallelStateMachine:
    def __init__(self, machines: List[StateMachine]):
        self.machines = machines
    
    async def run_async(self, **initial_data) -> List[DataContext]:
        """Run multiple workflows concurrently"""
        tasks = []
        for machine in self.machines:
            task = asyncio.create_task(self._run_machine_async(machine, **initial_data))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _run_machine_async(self, machine: StateMachine, **initial_data) -> DataContext:
        return machine.run(**initial_data)

# Usage: Run multiple analyses in parallel
analysis_machines = [
    StateMachine("sentiment_analysis", State.ANALYZE, State.COMPLETE, DataContext),
    StateMachine("keyword_extraction", State.ANALYZE, State.COMPLETE, DataContext),
    StateMachine("classification", State.ANALYZE, State.COMPLETE, DataContext)
]

parallel_machine = ParallelStateMachine(analysis_machines)
results = await parallel_machine.run_async(user_input="analyze this text")
```

**Benefits**: Performance improvement, independent processing, scalability
**Use Case**: Data analysis, batch processing, independent validations

### 5. **Enhanced Integration Manager**
Practical approach for your current setup:

```python
class IntegratedWorkflowManager:
    def __init__(self):
        self.machines = {}
    
    def register_machine(self, name: str, machine: StateMachine):
        self.machines[name] = machine
    
    def run_integrated(self, user_input: str) -> DataContext:
        """Smart routing with result integration"""
        
        # Step 1: Determine primary workflow
        if "sql" in user_input.lower() or "data" in user_input.lower():
            primary_result = self.machines["sql"].run(user_input=user_input)
            
            # Step 2: Enhance with chat formatting
            chat_result = self.machines["chat"].run(
                user_input=f"Format this SQL result: {primary_result.answer}"
            )
            
            # Step 3: Merge results
            primary_result.answer = f"{primary_result.answer}\n\nFormatted: {chat_result.answer}"
            primary_result.execution_trace.extend(["integrated_chat"] + chat_result.execution_trace)
            
            return primary_result
        else:
            return self.machines["chat"].run(user_input=user_input)

# Usage
manager = IntegratedWorkflowManager()
manager.register_machine("sql", sql_machine)
manager.register_machine("chat", chat_machine)

result = manager.run_integrated("show me sales data")
# Gets SQL result + chat formatting in one integrated response
```

## Integration Testing Strategies

### Test Individual Workflows
```python
def test_individual_workflows():
    """Test each workflow independently"""
    chat_result = chat_machine.run(user_input="hello")
    sql_result = sql_machine.run(user_input="show data")
    
    assert chat_result.answer.startswith("Chat")
    assert sql_result.sql_query is not None
```

### Test Integration Points
```python
def test_workflow_integration():
    """Test how workflows integrate together"""
    manager = IntegratedWorkflowManager()
    manager.register_machine("sql", sql_machine)
    manager.register_machine("chat", chat_machine)
    
    result = manager.run_integrated("sql query")
    
    # Should have both SQL and chat components
    assert "SQL:" in result.answer
    assert "Formatted:" in result.answer
    assert "integrated_chat" in result.execution_trace
```

### Test Error Propagation
```python
def test_error_propagation():
    """Test how errors propagate through integrated workflows"""
    # Mock a failing sub-workflow
    failing_machine = StateMachine("failing", State.ROUTER, State.COMPLETE, DataContext)
    
    with pytest.raises(Exception):
        composite.run_with_sub_machine(failing_machine, user_input="test")
```

## Integration Best Practices

### 1. **Context Management**
- Use shared DataContext across all workflows
- Merge execution traces for full visibility
- Handle context transformation between workflows

### 2. **Error Handling**
- Implement graceful fallbacks between workflows
- Propagate errors appropriately
- Maintain execution traces even during failures

### 3. **Performance Considerations**
- Use parallel execution for independent workflows
- Cache results when workflows are expensive
- Monitor execution times across integrated flows

### 4. **Testing Strategy**
- Test individual workflows first
- Test integration points separately
- Use mocks for expensive sub-workflows
- Test error scenarios and fallbacks

## Choosing Integration Patterns

| Pattern | Use Case | Complexity | Performance |
|---------|----------|------------|-------------|
| **Hierarchical** | Clear sub-processes | Medium | Good |
| **Pipeline** | Data transformation | Low | Good |
| **Orchestrator** | Dynamic routing | Medium | Excellent |
| **Parallel** | Independent processing | High | Excellent |
| **Manager** | Practical integration | Low | Good |

**Recommendation for BroInsight**: Start with the **Integration Manager** pattern for simplicity, then evolve to more complex patterns as needs grow.

This integration approach allows you to build complex, maintainable workflows while keeping individual components simple and testable.