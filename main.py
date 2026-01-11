from langchain_core.messages import HumanMessage
from src.graph import app

if __name__ == "__main__":
    print("--- AutoStream Agent CLI (Dev Mode) ---")
    
    state = {
        "messages": [],
        "lead_info": {"name": None, "email": None, "platform": None},
        "next_step": ""
    }
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        state["messages"].append(HumanMessage(content=user_input))
        result = app.invoke(state)
        state = result
        
        print(f"Agent: {state['messages'][-1].content}")