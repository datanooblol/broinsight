from . import Action, Shared
from brollm import BaseLLM

class GuideQuestion(Action):
    def __init__(self, system_prompt, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def run(self, shared:Shared):
        metadata = shared.metadata_loader.construct_prompt_context()
        user_chat_history = shared.user_input
        prompt = "METADATAS:\n\n{metadata}\n\nUSER_INPUT:\n\n{user_input}\n\n".format(metadata=metadata, user_input=user_chat_history)
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[
                self.model.UserMessage(text=prompt)
            ]
        )
        print("AI: {response}".format(response=response))
        shared.messages.append(self.model.AIMessage(text=response))
        return shared