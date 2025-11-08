from broinsight.statemachines.group_statemachine import StateGroup
from .specs import FlowState, FlowContext
from broinsight.agents.register import agent, AgentRegistry

router_flow = StateGroup("router_flow")

@agent("router_flow")
@router_flow.register(FlowState.ROUTER)
class RouterState:
    def next_state(self, context:FlowContext):
        if context.user_input.lower().startswith("/query"):
            context.user_input = context.user_input[len("/query"):].strip()
            return FlowState.SQL
        if context.user_input.lower().startswith("/guide"):
            context.user_input = context.user_input[len("/guide"):].strip()
            return FlowState.GUIDE

        if context.user_input.lower().startswith("/agents"):
            context.user_input = context.user_input[len("/agents"):].strip()
            print(AgentRegistry.list())
            return FlowState.COMPLETE
        return FlowState.CHAT
    def run(self, context:FlowContext):
        return self.next_state(context)