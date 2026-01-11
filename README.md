# AutoStream AI Agent 🤖

An intelligent conversational agent built for the ServiceHive ML Internship assignment. This agent is designed to automate lead qualification and customer support for the AutoStream SaaS platform.

## 🚀 Key Features
- **Intent Classification:** Distinguishes between Greetings, Product Inquiries (RAG), and Lead Capture.
- **Contextual RAG:** Retrieves pricing and policy details from a local knowledge base.
- **Agentic Workflow:** Uses `LangGraph` for state management and cyclic "slot-filling" logic.
- **Deployment Ready:** Includes a `Streamlit` UI for demos and a `FastAPI` webhook for WhatsApp integration.

## 🛠️ Architecture Explanation

### Why LangGraph?
I chose **LangGraph** over standard chains to implement a **cyclic state machine**. 
1. **State Management:** The agent maintains a persistent state (`AgentState`) tracking the conversation history and the `lead_info` dictionary (Name, Email, Platform).
2. **Cyclic Logic:** Unlike a linear chain, the **Lead Capture** node loops back on itself. If a user provides their name but forgets their email, the graph detects the missing slot and re-routes to the question node automatically. This ensures robust data collection without rigid if-else trees.

### Architecture Diagram
`User Input` -> `Intent Classifier` -> **Router**:
- **Path A (Inquiry):** -> `RAG Node` (Retrieves JSON data) -> End
- **Path B (High Intent):** -> `Lead Capture Node` <-> `Loop` (until all slots filled) -> `Tool Execution` -> End

## 📱 WhatsApp Deployment Strategy
The included `webhook.py` demonstrates how to deploy this agent to WhatsApp:
1. **Integration:** A **FastAPI** endpoint (`/whatsapp`) accepts `POST` requests from the Twilio API or Meta Cloud API.
2. **Session Handling:** In production, user state is stored in **Redis** keyed by the user's phone number (`sender_id`). The code provided uses an in-memory dictionary to simulate this.
3. **Async Execution:** The agent processes the input and returns the text response, which the API sends back to the user's WhatsApp chat.

## 💻 How to Run Locally

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
Create a .env file in the root directory:

```
GOOGLE_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

### 3. Run the UI (Recommended)
Launch the interactive "Glass Box" demo:

```
streamlit run app.py
```

### 4. Run the WhatsApp Webhook

```
python webhook.py
```
