from . import Action, Shared
from brollm import BaseLLM

class GenerateSQL(Action):
    def __init__(self, system_prompt:str, model:BaseLLM):
        super().__init__()
        self.system_prompt = system_prompt
        self.model = model

    def parse_response(self, response:str)->str:
        response = response.split("```sql")[-1].split("```")[0]
        return response

    def run(self, shared:Shared):
        selected_metadata = shared.metadata_loader.construct_prompt_context(shared.selected_metadata)
        user_input = shared.user_input
        prompt = "METADATAS:\n\n{selected_metadata}\n\nUSER_INPUT\n\n{user_input}".format(selected_metadata=selected_metadata, user_input=user_input)
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[self.model.UserMessage(text=prompt)]
        )
        shared.sql_query = self.parse_response(response)
        return shared