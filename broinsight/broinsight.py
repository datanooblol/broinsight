from brollm import BaseLLM
from .flow import get_flow
from .actions import Shared
from .metadata.metadata_loader import MetadataLoader
from typing import List, Dict, Any, Optional

class BroInsight:
    def __init__(self, model: BaseLLM, metadata_loader: Optional[MetadataLoader] = None, db: Optional[Any] = None):
        self.model = model
        self.metadata_loader = metadata_loader or MetadataLoader()
        self.db = db
        self.flow = get_flow(model)
    
    def ask(self, question: str, **kwargs) -> List[Dict[str, Any]]:
        """One-shot Q&A mode - ask a question and get the conversation messages back"""
        shared = Shared(
            user_input=question,
            metadata_loader=self.metadata_loader,
            db=self.db,
            method="ask",
            **kwargs
        )
        
        # Run the flow with pre-populated question
        self.flow.run(shared)
        response = shared.messages[-1]['content'][0]['text']
        print("AI: {response}".format(response=response))
        # Return the conversation messages
        return shared
    
    def chat(self, **kwargs):
        """Interactive chat mode - start a conversation session"""
        shared = Shared(
            metadata_loader=self.metadata_loader,
            db=self.db,
            method="chat",
            **kwargs
        )
        
        # Run the flow in interactive mode
        self.flow.run(shared)
        return shared