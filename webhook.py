from fastapi import FastAPI, Request, HTTPException
from langchain_core.messages import HumanMessage
from src.graph import app as agent_app

app = FastAPI()

# Key: User Phone Number, Value: AgentState
user_sessions = {}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook to receive messages from WhatsApp (via Twilio/Meta).
    """
    # 1. Parse incoming data (Standard Twilio format)
    form_data = await request.form()
    user_message = form_data.get("Body", "")
    sender_id = form_data.get("From", "unknown_user")

    if not user_message:
        return {"status": "ignored", "reason": "empty_message"}

    print(f" Received WhatsApp message from {sender_id}: {user_message}")

    # 2. Retrieve or Initialize State
    current_state = user_sessions.get(sender_id, {
        "messages": [],
        "lead_info": {"name": None, "email": None, "platform": None},
        "next_step": "greeting"
    })

    # 3. Add Message to State
    current_state["messages"].append(HumanMessage(content=user_message))

    # 4. Run Agent Logic
    result = agent_app.invoke(current_state)

    # 5. Update State Store
    user_sessions[sender_id] = {
        "messages": result["messages"],
        "lead_info": result["lead_info"],
        "next_step": result["next_step"]
    }

    # 6. Extract Bot Response
    bot_response = result["messages"][-1].content

    # 7. Return Response (Twilio expects TwiML, here we return JSON for demo)
    return {
        "response": bot_response, 
        "debug_next_step": result["next_step"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WhatsApp Webhook Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)