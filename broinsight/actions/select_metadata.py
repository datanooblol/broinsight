from . import Action, Shared
from brollm import BaseLLM
import yaml

class SelectMetadata(Action):
    def __init__(self, system_prompt:str, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def parse_response(self, response:str)->list:
        """This is a method for parsing"""
        response = response.split("```yaml")[-1].split("```")[0]
        response = yaml.safe_load(response)['tables']
        return response

    def run(self, shared:Shared):
        metadata = shared.metadata_loader.construct_prompt_context()
        user_chat_history = [m['content'][0]['text'] for m in shared.messages if m['role']=='user']
        user_chat_history = "\n".join(user_chat_history)
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_chat_history)
        messages = shared.messages.copy()
        messages.append(self.model.UserMessage(text=prompt))
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=messages
        )
        tables = self.parse_response(response)
        shared.selected_metadata = []
        for table in set(tables):
            shared.selected_metadata.append(table)
        return shared