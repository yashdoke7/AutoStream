import json
import os

def load_knowledge_base():
    """Loads the product data from JSON."""
    # Relative Pathing to the file
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, "data", "knowledge_base.json")
    
    with open(file_path, "r") as f:
        return json.load(f)

def mock_lead_capture(name: str, email: str, platform: str):
    """Simulates sending lead data to a backend CRM."""
    print(f"\n[SYSTEM ACTION] Lead captured successfully: {name}, {email}, {platform}\n")
    return "Success"