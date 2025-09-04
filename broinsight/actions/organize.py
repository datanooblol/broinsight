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
        elif response == "guide":
            return "guide"
        return "default"

    def run(self, shared:Shared):
        metadata = shared.metadata_loader.get_summary_prompt()
        user_input = shared.user_input
        shared.messages.append(self.model.UserMessage(text=user_input))
        user_chat_history = user_input
        # user_chat_history = [m['content'][0]['text'] for m in shared.messages if m['role']=='user']
        # user_chat_history = "\n".join(user_chat_history)
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_chat_history)
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[self.model.UserMessage(text=prompt)]
        )
        self.next_action = self.parse_response(response)
        return shared