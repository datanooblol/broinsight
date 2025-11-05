from typing import Optional
from broinsight.prompt_hub import PromptHub
from broinsight.utils.parse_string import parse_sql
from broinsight.core.llm import BaseLLM, ModelResponse, Role, UserMessage

class SQLAgent:
    def __init__(self, llm:BaseLLM):
        self.llm = llm

    def run(self, messages:list, system_prompt:Optional[str]=None)->ModelResponse:
        if system_prompt is None:
            system_prompt = PromptHub().generate_sql
        response = self.llm.run(system_prompt, messages)
        response.content = parse_sql(response.content)
        return response
