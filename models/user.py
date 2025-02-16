from typing import Dict, Any
import json
from pathlib import Path

def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get or create user profile."""
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    
    if str(user_id) not in users:
        users[str(user_id)] = {
            "balance": 0,
            "purchases_count": 0,
            "invited_friends": 0,
            "purchases": []
        }
        # Create users.json if it doesn't exist
        Path('data').mkdir(exist_ok=True)
        with open('data/users.json', 'w') as f:
            json.dump(users, f)
    
    return users[str(user_id)]

def update_user_profile(user_id: int, data: Dict[str, Any]) -> None:
    """Update user profile."""
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    
    users[str(user_id)] = data
    
    with open('data/users.json', 'w') as f:
        json.dump(users, f)
