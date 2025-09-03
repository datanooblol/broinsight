from broflow import Flow, Start, End
from .actions.user_input import UserInput
from .actions.retrieve import Retrieve
from .actions.chat import Chat
from .actions.generate_sql import GenerateSQL
from .actions.select_metadata import SelectMetadata
from .actions.organize import Organize
from brollm import BaseLLM
from broprompt import Prompt

def get_flow(model:BaseLLM):
    start_action = Start(message="Welcome to BroInsight!")
    end_action = End(message="Thank you for using BroInsight!")
    user_input_action = UserInput()
    organize_action = Organize(
        system_prompt=Prompt.from_markdown("broinsight/prompt_hub/organize.md").str,
        model=model
    )
    select_metadata_action = SelectMetadata(
        system_prompt=Prompt.from_markdown("broinsight/prompt_hub/select_metadata.md").str,
        model=model
    )
    generate_sql_action = GenerateSQL(
        system_prompt=Prompt.from_markdown("broinsight/prompt_hub/generate_sql.md").str,
        model=model
    )
    retrieve_action = Retrieve()
    chat_action = Chat(
        system_prompt=Prompt.from_markdown("broinsight/prompt_hub/chat.md").str,
        model=model
    )
    start_action >> user_input_action
    user_input_action >> organize_action
    organize_action -"select_metadata">> select_metadata_action
    select_metadata_action >> generate_sql_action
    generate_sql_action >> retrieve_action
    retrieve_action >> chat_action
    organize_action >> chat_action
    chat_action >> user_input_action
    user_input_action -"exit">> end_action
    return Flow(start_action=start_action, name="BroInsight Start!")