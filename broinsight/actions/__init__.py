from broflow import Action
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from brollm import BaseLLM
from broinsight.metadata.metadata_loader import MetadataLoader
from dataclasses import field

class Shared(BaseModel):
    user_input:str = Field(description="User input", default="")
    metadata_loader:Any = Field(description="Metadata Loader", default=None)
    selected_metadata:List[str] = Field(description="Selected metadata", default_factory=list)
    sql_query:str = Field(description="SQL query", default="")
    query_result:Any = Field(description="Query result", default=None)
    messages:List[Dict[str, Any]] = Field(description="Messages", default_factory=list)
    db: Any = Field(description="Connection", default=None)
    method: Literal["ask", "chat"] = Field(description="Method", default="ask")
    error_log:List[str] = Field(description="Error Log", default_factory=list)
    retries:int = Field(description="Retries", default=0)
    max_retries:int = Field(description="Max retries", default=3)
    fallback_message:Any = Field(description="Fallback message", default=None)