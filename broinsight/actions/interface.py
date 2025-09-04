from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from broinsight.session_logger import SessionLogger

class Shared(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: Any = Field(description="LLM model")
    messages: List[Dict[str, Any]] = Field(description="Messages")
    
    db: Any = Field(description="Data connection for queries", default=None)
    metadata_db: Any = Field(description="Metadata database connection", default=None)

    selected_metadata: List[str] = Field(description="Selected metadata", default_factory=list)
    sql_query: str = Field(description="SQL query", default="")
    query_result: Any = Field(description="Query result", default=None)
    error_log: List[str] = Field(description="Error Log", default_factory=list)
    retries: int = Field(description="Retries", default=0)
    max_retries: int = Field(description="Max retries", default=3)
    fallback_message: Any = Field(description="Fallback message", default=None)
    
    # Session support
    session_logger: Optional[SessionLogger] = Field(description="Session logger", default=None)
    input_token: int = Field(description="Input token", default=0)
    output_token: int = Field(description="Output token", default=0)
    
    def model_post_init(self, __context):
        """Initialize session_logger after object creation"""
        if self.session_logger is None:
            self.session_logger = SessionLogger()