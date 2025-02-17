from typing import Dict, Any
import json
from pathlib import Path

def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Получение или создание профиля пользователя."""
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
        # Создание users.json, если файл не существует
        Path('data').mkdir(exist_ok=True)
        with open('data/users.json', 'w') as f:
            json.dump(users, f)

    return users[str(user_id)]

def update_user_profile(user_id: int, profile: Dict[str, Any]) -> None:
    """Обновление профиля пользователя."""
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)

        users[str(user_id)] = profile

        with open('data/users.json', 'w') as f:
            json.dump(users, f)
    except Exception as e:
        raise ValueError(f"Ошибка при обновлении профиля: {str(e)}")
