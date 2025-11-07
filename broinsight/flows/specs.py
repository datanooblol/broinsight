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

class BaseContext(BaseModel):
    response: Optional[ModelResponse] = Field(default=None)

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
    catalog:Any = Field(default=None)
    execution_trace:List[Dict[str, Any]] = Field(default_factory=list)