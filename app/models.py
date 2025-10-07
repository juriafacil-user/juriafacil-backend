from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# -------------------------------
# 🔹 Funções para serializar usuários do MongoDB
# -------------------------------
def user_entity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "plan": user.get("plan", "free"),
        "upload_count": user.get("upload_count", 0),
        "last_upload": user.get("last_upload"),
        "plan_expiration": user.get("plan_expiration")
    }

def users_entity(users) -> list:
    return [user_entity(user) for user in users]

# -------------------------------
# 🔹 Modelo Pydantic para criação/validação
# -------------------------------
class UserModel(BaseModel):
    id: Optional[str]
    name: str
    email: EmailStr
    password: Optional[str] = None
    plan: str = "free"                # free | premium
    upload_count: int = 0             # quantos uploads o usuário já fez
    last_upload: Optional[datetime] = None
    plan_expiration: Optional[datetime] = None


