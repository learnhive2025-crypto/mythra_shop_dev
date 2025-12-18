from datetime import datetime

def user_model(username, email, password, role, is_active=True):
    return {
        "username": username,
        "email": email,
        "password": password,
        "role": role,  # SUPER_ADMIN | ADMIN | STAFF
        "is_active": is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None
    }
