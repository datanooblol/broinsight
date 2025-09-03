from brollm import BaseLLM

class TableDescriptor:
    def __init__(self, system_prompt:str, model:BaseLLM):
        # super().__init__()
        self.system_prompt = system_prompt
        self.model = model
    def parse_response(self, response):
        response = response.split("```text")[-1].split("```")[0]
        return response
    
    def run(self, metadata:dict):
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[
                self.model.UserMessage(text=metadata)
            ]
        )
        response = self.parse_response(response)
        return response