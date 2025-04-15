import os
import json
from datetime import datetime

BASE_SAVE_DIR = "saved_projects"

def save_project(description, history, timeline, metamemory):
    os.makedirs(BASE_SAVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"project_{timestamp}.json"
    path = os.path.join(BASE_SAVE_DIR, filename)

    data = {
        "description": description,
        "history": history,
        "timeline": timeline,
        "metamemory": metamemory,
        "saved_at": timestamp
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename

def list_saved_projects():
    if not os.path.exists(BASE_SAVE_DIR):
        return []
    return [f for f in os.listdir(BASE_SAVE_DIR) if f.endswith(".json")]

def load_project(filename):
    path = os.path.join(BASE_SAVE_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)