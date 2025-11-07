from broinsight.statemachines.group_statemachine import StateGroup
from broinsight.prompt_hub import PromptHub
from broinsight.core.llm import LocalOpenAI, UserMessage
from broinsight.utils.parse_string import parse_sql
from .specs import FlowState, FlowContext
from broinsight.utils.register import agent
sql_flow = StateGroup("sql_flow")

@agent("sql_flow")
@sql_flow.register(FlowState.SQL)
class SQLFlow:
    def __init__(self): self.llm = LocalOpenAI()
    def next_state(self): return FlowState.CHAT
    def get_content(self, context:FlowContext):
        metadata = context.catalog.query("DESCRIBE tips;").loc[:, ['column_name', 'column_type']]
        content = [f"METADATAS: TABLE name's tips\n\n{metadata.to_string()}\n\n"]
        content.append(f"USER_INPUT:\n\n{context.user_input}\n\n")
        return "\n".join(content)
    def run(self, context: FlowContext):
        chat_history = context.chat.chat_history
        content = self.get_content(context)
        response = self.llm.run(PromptHub().generate_sql, chat_history+[UserMessage(content=content)])
        context.sql.response = response
        sql_query = parse_sql(response.content)
        context.sql.sql = sql_query
        query_result = context.catalog.query(sql_query)
        context.sql.data = query_result
        return self.next_state()