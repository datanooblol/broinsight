from . import Action, Shared, BaseLLM
import pandas as pd

class Chat(Action):
    def __init__(self, system_prompt:str, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def create_prompt(self, shared:Shared):
        if shared.query_result is None:
            prompt = shared.user_input
        elif shared.fallback_message is not None:
            prompt = f"{shared.fallback_message}\n\nUser question: {shared.user_input}\n\nPlease explain what went wrong and suggest how to rephrase the question."
        else:
            prompt = [
                "DATA:\n\n{result}\n\n".format(result=shared.query_result.to_string(index=False, max_cols=None)),
                "USER_INPUT:\n\n{user_input}".format(user_input=shared.user_input)
            ]
            prompt = "\n".join(prompt)
        return prompt

    def run(self, shared:Shared):
        prompt = self.create_prompt(shared)
        
        # Create temporary messages for LLM call
        temp_messages = shared.messages[:-1].copy() + [self.model.UserMessage(text=prompt)]
        
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=temp_messages
        )
        
        # Add the actual conversation to shared messages
        shared.messages.append(self.model.AIMessage(text=response))
        
        if shared.method == "chat":
            print("AI: {response}".format(response=response))
        if shared.method == "ask":
            shared.user_input = "/exit"
        
        # Clear query result for next iteration in interactive mode
        shared.query_result = None
        shared.fallback_message = None
        
        return shared