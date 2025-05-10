from fastapi import HTTPException, status

def get_current_user():
    # TODO: replace with real auth (JWT/OAuth)
    return {"user_id": "anonymous"}