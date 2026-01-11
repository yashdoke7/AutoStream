import streamlit as st
import json
from langchain_core.messages import HumanMessage, AIMessage
from src.graph import app as agent_app 

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AutoStream Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stChatMessage { background-color: white; border: 1px solid #e0e0e0; border-radius: 10px; }
    .json-box { font-family: monospace; font-size: 0.85em; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🤖 AutoStream AI Agent")
st.markdown("### Intelligent Lead Capture & Support System")

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(AIMessage(content="Hello! I'm the AutoStream assistant. How can I help you today?"))

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "lead_info": {"name": None, "email": None, "platform": None},
        "next_step": "greeting"
    }

# --- LAYOUT: 2 COLUMNS ---
chat_col, brain_col = st.columns([2, 1], gap="large")

# --- COLUMN 2: THE BRAIN ---
with brain_col:
    st.subheader("🧠 Agent Internals")
    st.info("Live view of the Agent's state memory and decision logic.")
    
    st.markdown("**1. Lead Capture Slots:**")
    st.json(st.session_state.agent_state.get("lead_info", {}))
    
    st.markdown("**2. Current Intent / Node:**")
    current_step = st.session_state.agent_state.get("next_step", "Unknown")
    
    if current_step == "high_intent":
        st.error(f"🔴 Intent: {current_step} (Action Required)")
    elif current_step == "inquiry":
        st.success(f"🟢 Intent: {current_step} (RAG Retrieval)")
    else:
        st.warning(f"🟡 Intent: {current_step} (Conversational)")

    with st.expander("📚 Knowledge Base Context (RAG)"):
        try:
            with open("data/knowledge_base.json", "r") as f:
                st.json(json.load(f))
        except:
            st.text("Data file not found")

# --- COLUMN 1: THE CHAT ---
with chat_col:
    # Display history
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"): st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"): st.write(msg.content)

    # Input handling
    if user_input := st.chat_input("Type your message..."):
        with st.chat_message("user"): st.write(user_input)
        st.session_state.messages.append(HumanMessage(content=user_input))
        
        # Invoke Agent
        inputs = {
            "messages": st.session_state.messages,
            "lead_info": st.session_state.agent_state["lead_info"],
            "next_step": st.session_state.agent_state["next_step"]
        }
        
        result = agent_app.invoke(inputs)
        
        # Update State
        bot_response = result["messages"][-1]
        st.session_state.messages.append(bot_response)
        st.session_state.agent_state = {
            "lead_info": result["lead_info"],
            "next_step": result["next_step"]
        }
        st.rerun()