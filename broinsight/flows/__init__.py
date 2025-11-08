from broinsight.statemachines.group_statemachine import CompositeStateGroup
from .router_flow import router_flow
from .chat_flow import chat_flow
from .sql_flow import sql_flow
from .guide_flow import guide_flow
from .tool_state import tool_flow
from .specs import FlowState, FlowContext

combined_app = CompositeStateGroup("combined", router_flow, chat_flow, sql_flow, guide_flow, tool_flow)