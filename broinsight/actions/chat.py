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
        else:
            prompt = [
                "DATA:\n\n{result}\n\n".format(result=shared.query_result.to_string(index=False, max_cols=None)),
                "USER_INPUT:\n\n{user_input}".format(user_input=shared.user_input)
            ]
            prompt = "\n".join(prompt)
        return prompt

    def run(self, shared:Shared):
        messages = shared.messages
        prompt = self.create_prompt(shared)
        messages.append(self.model.UserMessage(text=prompt))
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=messages
        )
        messages.append(self.model.AIMessage(text=response))
        print("AI: {response}".format(response=response))
        shared.query_result = pd.DataFrame()
        return shared