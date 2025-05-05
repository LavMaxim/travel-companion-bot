from collections import defaultdict

# {user_id: {"date": ..., "purpose": ..., "companions": ..., "location": ...}}
user_filters = {}
pagination_state = {}

def set_filter(user_id: int, key: str, value: str):
    user_filters[user_id][key] = value

def get_filters(user_id: int) -> dict:
    return user_filters.get(user_id, {})

def clear_filters(user_id: int):
    if user_id in user_filters:
        user_filters[user_id] = {}

def filters_to_string(user_id: int) -> str:
    f = get_filters(user_id)
    parts = []
    for k, v in f.items():
        parts.append(f"{k.capitalize()}: {v}")
    return " | ".join(parts) if parts else "—"


user_filters = {}
pagination_state = {}