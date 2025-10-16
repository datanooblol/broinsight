import boto3
import time
from pydantic import BaseModel
from typing import Optional, Any

class AWSConfig(BaseModel):
    aws_access_key_id:str
    aws_secret_access_key:str
    aws_session_token:Optional[str] = None
    region_name:str = 'us-west-2'

# class BaseLLM:
#     def __init__(self, *args, **kwargs): pass
#     def UserMessage(self, text): pass
#     def AIMessage(self, text): pass
#     def SystemMessage(self, text): pass
#     def OutputMessage(self, text): pass
#     def run(self, system_prompt, messages): pass

class BedrockOpenAI:
    def __init__(self, model_id, aws_configs, temperature=0.1):
        self.model_id = model_id
        self.aws_configs = self._validate_config(aws_configs)
        self.temperature = temperature
    
    def _validate_config(self, aws_configs):
        """Validate and convert AWSConfig to dictionary"""
        if isinstance(aws_configs, AWSConfig):
            return aws_configs.model_dump()
        elif isinstance(aws_configs, dict):
            # Validate dict has required fields
            AWSConfig(**aws_configs)  # This will raise ValidationError if invalid
            return aws_configs
        else:
            raise TypeError("aws_configs must be AWSConfig instance or dict")

    def get_model(self):
        model = boto3.client(
            service_name='bedrock-runtime',
            **self.aws_configs
        )
        return model
    def SystemMessage(self, text):
        return [{"text": text}]
    
    def UserMessage(self, text):
        return {"role":"user", "content": [{"text": text}]}
    
    def AIMessage(self, text):
        return {"role":"user", "content": [{"text": text}]}
    
    def OutputMessage(self, response):
        return dict(
            content=[i['text'] for i in response['output']['message']['content'] if 'text' in i][-1],
            model=self.model_id,
            processed=response['processed'],
            tokens=dict(
                input=response['usage']["inputTokens"],
                output=response['usage']["outputTokens"]
            )
        )

    def run(self, system_prompt, messages):
        start = time.time()
        model = self.get_model()
        response = model.converse(
            modelId=self.model_id,
            system=self.SystemMessage(system_prompt),
            messages=messages,
            inferenceConfig=dict(
                temperature=self.temperature
            )
        )
        response['processed'] = time.time() - start
        response = self.OutputMessage(response=response)
        return response