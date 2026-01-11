import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from src.state import AgentState
from src.utils import load_knowledge_base, mock_lead_capture

# Initialize LLM
# Ensure OPENAI_API_KEY is in your environment variables
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

KNOWLEDGE_BASE = load_knowledge_base()

def intent_classifier_node(state: AgentState):
    """
    Analyzes the LAST user message to determine intent.
    Categories: Greeting, Product Inquiry, High Intent.
    """
    last_message = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are an intent classifier for AutoStream, a video editing SaaS.
        Classify the user's message into exactly one of these three categories:
        1. "greeting" (e.g., Hi, Hello)
        2. "inquiry" (e.g., pricing, features, refund policy, comparisons)
        3. "high_intent" (e.g., I want to sign up, I want the pro plan, ready to buy)

        User Message: {message}
        
        Respond ONLY with the category name.
        """
    )
    chain = prompt | llm
    response = chain.invoke({"message": last_message})
    intent = response.content.strip().lower()
    
    return {"next_step": intent}

def rag_node(state: AgentState):
    """
    Handles product inquiries using the loaded JSON data.
    """
    query = state["messages"][-1].content
    context_str = json.dumps(KNOWLEDGE_BASE, indent=2)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful support agent for AutoStream. 
        Answer the user's question based ONLY on the following context.
        
        Context:
        {context}
        
        User Question: {question}
        """
    )
    chain = prompt | llm
    response = chain.invoke({"context": context_str, "question": query})
    
    return {"messages": [response], "next_step": "end"}

def lead_capture_node(state: AgentState):
    """
    Checks what info is missing and asks for it.
    """
    current_info = state.get("lead_info", {})
    last_message = state["messages"][-1].content
    
    # Update state if we are already collecting
    if state.get("next_step") == "collecting":
        extraction_prompt = ChatPromptTemplate.from_template(
            """
            Extract lead information from the user's message.
            Current known info: {current_info}
            User message: {message}
            
            Return a JSON object merging the new info. 
            Keys must be: "name", "email", "platform".
            """
        )
        extractor = extraction_prompt | llm
        result = extractor.invoke({"current_info": json.dumps(current_info), "message": last_message})
        try:
            content = result.content.strip().replace("```json", "").replace("```", "")
            current_info.update(json.loads(content))
        except:
            pass

    # Check missing fields
    required_fields = ["name", "email", "platform"]
    missing = [field for field in required_fields if not current_info.get(field)]
    
    if not missing:
        return {"lead_info": current_info, "next_step": "execute_tool"}
    
    # Ask for next field
    next_field = missing[0]
    questions = {
        "name": "Great! Let's get you set up. What is your full name?",
        "email": "Thanks. What is your email address?",
        "platform": "Almost done! Which creator platform do you use? (e.g., YouTube, Instagram)"
    }
    
    return {"messages": [AIMessage(content=questions[next_field])], "lead_info": current_info, "next_step": "collecting"}

def tool_execution_node(state: AgentState):
    """Executes the mock API call."""
    info = state["lead_info"]
    mock_lead_capture(info["name"], info["email"], info["platform"])
    
    confirm_msg = AIMessage(content=f"Thanks {info['name']}! Registered interest for {info['platform']}. We will contact {info['email']}.")
    return {"messages": [confirm_msg], "next_step": "end"}

def greeting_node(state: AgentState):
    return {"messages": [AIMessage(content="Hello! I'm the AutoStream assistant. How can I help you today?")], "next_step": "end"}