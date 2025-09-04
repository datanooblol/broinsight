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
        user_chat_history = [m['content'][0]['text'] for m in shared.messages if m['role']=='user']
        user_chat_history = "\n".join(user_chat_history)
        prompt = "METADATAS:\n\n{selected_metadata}\n\nUSER_INPUT\n\n{user_input}".format(selected_metadata=selected_metadata, user_input=user_chat_history)
        if len(shared.error_log)>0:
            prompt += "IMPORTANT: avoid the below errors\n\n{errors}".format(errors="\n".join(["\t- {err}".format(err=err) for err in shared.error_log]))
        response = self.model.run(
            system_prompt=self.system_prompt,
            messages=[self.model.UserMessage(text=prompt)]
        )
        shared.sql_query = self.parse_response(response)
        return shared