from broinsight.statemachines.group_statemachine import StateGroup
from .specs import FlowState, FlowContext
from broinsight.agents.register import agent, AgentRegistry
from broinsight.prompt_hub import PromptHub
from broinsight.core.llm import LocalOpenAI, UserMessage, AIMessage, ModelResponse
from sentence_transformers import SentenceTransformer
import numpy as np
from broinsight.tools.register import ToolBox
import broinsight.tools.tools
from sentence_transformers import CrossEncoder
from broinsight.utils.parse_string import parse_json, parse_blockcode
import json
# Load a pretrained CrossEncoder model
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
# Load once, reuse many times
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(user_input: str, tool_texts: list) -> np.ndarray:
    # Encode all at once (faster than individual calls)
    all_texts = [user_input] + tool_texts
    embeddings = embedder.encode(all_texts)
    
    user_emb = embeddings[0]
    tool_embs = embeddings[1:]
    
    # Cosine similarity
    similarities = np.dot(tool_embs, user_emb) / (
        np.linalg.norm(tool_embs, axis=1) * np.linalg.norm(user_emb)
    )
    
    return similarities

tool_flow = StateGroup("tool_flow")

@agent("tool_logic")
@tool_flow.register(FlowState.IS_TOOL)
class ToolLogicState:
    def next_state(self, logic:bool):
        if logic:
            return FlowState.TOOL_FILTER
        return FlowState.ROUTER
    def run(self, context:FlowContext):
        tools = ToolBox.list_tool_metadata()
        print(tools)
        user_input = context.user_input
        scores = calculate_similarity(user_input, tools)
        logic = any(scores>0.3)
        print(logic, scores)
        context.tool.is_tool = logic
        return self.next_state(logic)

@tool_flow.register(FlowState.TOOL_FILTER)
class ToolFilterState:
    def next_state(self):
        return FlowState.TOOL_SELECTION
    def run(self, context:FlowContext):
        user_input = context.user_input
        tools = ToolBox.list_tool_metadata()
        ranks = reranker.rank(user_input, tools, return_documents=True)
        candidated_tools = [r['text'].split(" ")[0] for r in ranks[:5]]
        context.tool.candidated_tools = candidated_tools
        return self.next_state()

@tool_flow.register(FlowState.TOOL_SELECTION)
class ToolSelectionState:
    def __init__(self): self.llm = LocalOpenAI()
    def next_state(self):
        return FlowState.TOOL_PARSING
    def run(self, context:FlowContext):
        candidated_tools = context.tool.candidated_tools
        user_input = context.user_input
        content = f"AVAILABLE_TOOLS:\n\n{ToolBox.prompt(candidated_tools)}\n\nUSER_INPUT:\n\n{user_input}\n\n"
        response = self.llm.run(PromptHub().tool_selection, messages=[UserMessage(content=content)])
        context.tool.selection_response = response
        context.tool.selected_tool = json.loads(parse_json(response.content))['selected_tool']
        return self.next_state()

@tool_flow.register(FlowState.TOOL_PARSING)    
class ToolParsingState:
    def __init__(self): self.llm = LocalOpenAI()
    def nex_state(self):
        return FlowState.COMPLETE
    def run(self, context:FlowContext):
        user_input = context.user_input
        tool_prompt = ToolBox.tool_prompt(context.tool.selected_tool)
        content = f"TOOLS:\n\n{tool_prompt}\n\nUSER_INPUT:\n\n{user_input}\n\n"
        response = self.llm.run(PromptHub().tool_parsing, messages=[UserMessage(content=content)])
        context.tool.tool_parsing_response = response
        return self.nex_state()
