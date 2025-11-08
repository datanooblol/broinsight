from broinsight.statemachines.group_statemachine import StateGroup
from broinsight.prompt_hub import PromptHub
from broinsight.core.llm import LocalOpenAI, UserMessage, AIMessage
from .specs import FlowState, FlowContext
from broinsight.agents.register import agent

guide_flow = StateGroup("guide_flow")

@agent("guide_flow")
@guide_flow.register(FlowState.GUIDE)
class ChatState:
    def __init__(self): self.llm = LocalOpenAI()
    def next_state(self): return FlowState.COMPLETE
    def get_content(self, context:FlowContext):
        metadata = context.catalog.query("DESCRIBE tips;").loc[:, ['column_name', 'column_type']]
        content = [f"METADATAS: TABLE name's tips\n\n{metadata.to_string()}\n\n"]
        content.append(f"USER_INPUT:\n\n{context.user_input}\n\n")
        return "\n".join(content)
    
    def run(self, context: FlowContext):
        chat_history = context.chat.chat_history
        content = self.get_content(context)
        response = self.llm.run(PromptHub().guide_question, chat_history+[UserMessage(content=content)])
        chat_history.append(UserMessage(content=context.user_input))
        chat_history.append(AIMessage(content=response.content))
        context.chat.chat_history = chat_history
        context.chat.response = response
        return self.next_state()