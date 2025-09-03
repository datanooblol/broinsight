from . import Action, Shared
from brollm import BaseLLM
import yaml

class Organize(Action):
    def __init__(self, system_prompt:str, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def parse_response(self, response:str):
        """This is a method for parsing"""
        response = response.split("```yaml")[-1].split("```")[0]
        response = yaml.safe_load(response)['direct_to']
        if response == "query":
            return "select_metadata"
        return "default"

    def run(self, shared:Shared):
        metadata = shared.metadata_loader.get_summary_prompt()
        # metadata = shared.metadata_loader.construct_prompt_context()
        user_input = shared.user_input
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_input)
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[self.model.UserMessage(text=prompt)]
        )
        self.next_action = self.parse_response(response)
        return shared