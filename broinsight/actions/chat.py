from . import Action, BaseLLM
from .interface import Shared

class Chat(Action):
    def __init__(self, system_prompt:str, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def create_prompt(self, shared:Shared):
        user_input = shared.messages[-1]['content']
        if shared.query_result is None:
            prompt = user_input
        elif shared.fallback_message is not None:
            prompt = f"{shared.fallback_message}\n\nUser question: {user_input}\n\nPlease explain what went wrong and suggest how to rephrase the question."
        else:
            prompt = [
                "DATA:\n\n{result}\n\n".format(result=shared.query_result.to_string(index=False, max_cols=None)),
                "USER_INPUT:\n\n{user_input}".format(user_input=user_input)
            ]
            prompt = "\n".join(prompt)
        return prompt

    def run(self, shared:Shared):
        prompt = self.create_prompt(shared)
        
        # Create temporary messages for LLM call
        temp_messages = shared.messages[:-1].copy() + [self.model.UserMessage(text=prompt)]
        try:
            response = self.model.run(
                system_prompt=self.system_prompt,
                messages=temp_messages
            )
            shared.input_token += response['tokens']['input']
            shared.output_token += response['tokens']['output']
            # Add the actual conversation to shared messages
            shared.messages.append(self.model.AIMessage(text=response['content']))
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, output_data=response['content'], status='success'
            )
        except Exception as e:
            shared.session_logger.log(
                action=self.__class__.__name__, input_data=prompt, status='failed', error_message=str(e)
            )            
        return shared