import boto3
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum
import time
import requests

def bedrock_driver(messages):
    return [dict(role=m['role'], content=[dict(text=m['content'])]) for m in messages]

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ModelResponse(BaseModel):
    model_name: str
    role: Role
    content: str
    reason: str
    input_tokens: int
    output_tokens: int
    response_time_ms: int
    id: str = Field(default_factory=lambda: str(uuid4()))

def UserMessage(content:str)->dict:
    return dict(role='user', content=content)

class BaseLLM(ABC):
    def __init__(self, model_id,):
        self.model_id = model_id
    
    @abstractmethod
    def OutputMessage(self, response:dict, response_time_ms:int) -> ModelResponse:
        """Abstract method to be implemented by child classes"""
        pass

    @abstractmethod
    def run(self, system_prompt:str, messages:list)->ModelResponse:
        """Abstract method to be implemented by child classes"""
        pass

class BaseBedrock(BaseLLM):
    def __init__(self, model_id):
        super().__init__(model_id)

    def get_model(self):
        return boto3.client('bedrock-runtime', region_name='us-east-1')

    def bedrock_driver(self, messages):
        return [dict(role=m['role'], content=[dict(text=m['content'])]) for m in messages]
    
    def run(self, system_prompt:str, messages:list)->ModelResponse:
        model = self.get_model()
        start_time = time.time()
        response = model.converse(
            modelId=self.model_id,
            messages=self.bedrock_driver(messages),
            system=[{"text": system_prompt}]
        )
        response_time_ms = int((time.time() - start_time) * 1000)
        return self.OutputMessage(response, response_time_ms)
    
class BedrockOpenAI(BaseBedrock):
    def __init__(self, model_id="openai.gpt-oss-20b-1:0"):
        super().__init__(model_id)

    def OutputMessage(self, response, response_time_ms)->ModelResponse:
        proxy = response['output']['message']
        usage = response['usage']
        return ModelResponse(
            model_name=self.model_id,
            role=proxy['role'],
            content=proxy['content'][-1]['text'],
            reason=proxy['content'][0]['reasoningContent']['reasoningText']['text'],
            input_tokens=usage['inputTokens'],
            output_tokens=usage['outputTokens'],
            response_time_ms=response_time_ms
        )
    
class LocalOpenAI(BaseLLM):
    def __init__(self, model_id="gpt-oss:20b"):
        super().__init__(model_id=model_id)
        self.endpoint_url: str = "http://localhost:11434/api/chat"

    def OutputMessage(self, response, response_time_ms)->ModelResponse:
        return ModelResponse(
            model_name=response['model'],
            role=response['message']['role'],
            content=response['message']['content'],
            reason=response['message']['thinking'],
            input_tokens=0,
            output_tokens=0,
            response_time_ms=response_time_ms
        )

    def run(self, system_prompt:str, messages:list)->ModelResponse:
        start_time = time.time()
        payload = {
            "model": self.model_id,
            "messages": [dict(role="system", content=system_prompt)]+messages,
            "stream": False
        }
        response = requests.post(self.endpoint_url, json=payload)
        response_time_ms = int((time.time() - start_time) * 1000)
        return self.OutputMessage(response.json(), response_time_ms=response_time_ms)