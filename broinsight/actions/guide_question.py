from . import Action, BaseLLM
from .interface import Shared

class GuideQuestion(Action):
    def __init__(self, system_prompt, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def run(self, shared:Shared):
        metadata = shared.metadata_db.construct_prompt_context()
        user_chat_history = shared.messages[-1]['content']
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_chat_history)
        try:
            response = self.model.run(
                system_prompt=self.system_prompt,
                messages=[
                    self.model.UserMessage(text=prompt)
                ]
            )
            shared.input_token += response['tokens']['input']
            shared.output_token += response['tokens']['output']        
            shared.messages.append(self.model.AIMessage(text=response['content']))
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, output_data=response['content'], status='success'
            )
        except Exception as e:
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, status='failed', error_message=str(e)
            )            
        return shared