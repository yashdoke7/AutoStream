from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import (
    intent_classifier_node, 
    rag_node, 
    lead_capture_node, 
    tool_execution_node, 
    greeting_node
)

# Define Router Logic
def router(state: AgentState):
    step = state["next_step"]
    if step == "greeting": return "greeting_agent"
    elif step == "inquiry": return "rag_agent"
    elif step == "high_intent": return "lead_collector"
    elif step == "collecting": return "lead_collector"
    elif step == "execute_tool": return "tool_executor"
    else: return "greeting_agent"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("classifier", intent_classifier_node)
workflow.add_node("rag_agent", rag_node)
workflow.add_node("greeting_agent", greeting_node)
workflow.add_node("lead_collector", lead_capture_node)
workflow.add_node("tool_executor", tool_execution_node)

workflow.set_entry_point("classifier")

workflow.add_conditional_edges(
    "classifier",
    router,
    {
        "greeting_agent": "greeting_agent",
        "rag_agent": "rag_agent",
        "lead_collector": "lead_collector"
    }
)

workflow.add_conditional_edges(
    "lead_collector",
    router,
    {
        "lead_collector": "lead_collector",
        "tool_executor": "tool_executor"
    }
)

workflow.add_edge("greeting_agent", END)
workflow.add_edge("rag_agent", END)
workflow.add_edge("tool_executor", END)

# Compile
app = workflow.compile()