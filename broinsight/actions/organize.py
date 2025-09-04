from . import Action, BaseLLM
from .interface import Shared
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
        # Add user input to messages if not already there
        if shared.db is None and shared.metadata_db is None:
            return shared
        
        metadata = shared.metadata_db.get_summary_prompt()

        user_input = shared.messages[-1]['content']
        
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_input)
        try:
            response = self.model.run(
                system_prompt=self.system_prompt,
                messages=[self.model.UserMessage(text=prompt)]
            )
            shared.input_token += response['tokens']['input']
            shared.output_token += response['tokens']['output']        
            self.next_action = self.parse_response(response['content'])
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, output_data=response['content'], status='success'
            )
        except Exception as e:
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, status='failed', error_message=str(e)
            )            
        return shared