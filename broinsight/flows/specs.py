from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from broinsight.core.llm import ModelResponse

class FlowState(Enum):
    ROUTER = "router"
    GUIDE = "guide"
    CHAT = "chat"
    SQL = "sql"
    COMPLETE = "complete"
    IS_TOOL = "is_tool"
    TOOL_FILTER = "tool_filter"
    TOOL_SELECTION = "tool_selection"
    TOOL_PARSING = "tool_parsing"

class AIThought(Enum):
    """Everytime AI response, we should know its thought that this response does like this response aims to validate something or it's a result and need new request"""
    NEW_REQUEST = "new_request"
    AWAITING_RESPONSE = "awaiting_response"

class BaseContext(BaseModel):
    response: Optional[ModelResponse] = Field(default=None)

class ToolContext(BaseContext):
    is_tool:Optional[bool] = Field(default=False)
    is_tool_response:Optional[ModelResponse] = Field(default=None)
    candidated_tools:Optional[List[str]] = Field(default=None)
    selection_response:Optional[ModelResponse] = Field(default=None)
    selected_tool:Optional[str] = Field(default=None)
    tool_parsing_response:Optional[ModelResponse] = Field(default=None) 

class RouterContext(BaseContext):
    route:Optional[str] = Field(default=None)

class SQLContext(BaseContext):
    sql:Optional[str] = Field(default=None)
    data:Optional[Any] = Field(default=None)

class ChatContext(BaseContext):
    chat_history:List[Dict[str, Any]] = Field(default_factory=list)

class FlowContext(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    user_input:str
    router:RouterContext = Field(default_factory=RouterContext)
    chat:ChatContext = Field(default_factory=ChatContext)
    sql:SQLContext = Field(default_factory=SQLContext)
    tool:ToolContext = Field(default_factory=ToolContext)
    catalog:Any = Field(default=None)
    ai_thought:AIThought = Field(default=AIThought.NEW_REQUEST)
    execution_trace:List[Dict[str, Any]] = Field(default_factory=list)