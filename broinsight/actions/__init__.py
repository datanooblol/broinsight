from broflow import Action
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from brollm import BaseLLM
from broinsight.metadata.metadata_loader import MetadataLoader

class Shared(BaseModel):
    user_input:str = Field(description="User input", default="")
    metadata_loader:Any = Field(description="Metadata Loader", default=None)
    selected_metadata:List[str] = Field(description="Selected metadata", default_factory=list)
    sql_query:str = Field(description="SQL query", default="")
    query_result:Any = Field(description="Query result", default=None)
    messages:List[Dict[str, Any]] = Field(description="Messages", default_factory=list)
    db: Any = Field(description="Connection", default=None)