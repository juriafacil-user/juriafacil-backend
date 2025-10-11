from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# -------------------------------
# 🔹 Serializers (Mongo -> JSON)
# -------------------------------
def plan_entity(plan) -> dict:
    if not plan:
        return None
    return {
        "id": str(plan.get("_id")) if plan.get("_id") else None,
        "code": plan.get("code"),
        "name": plan.get("name"),
        "price": plan.get("price"),
        "currency": plan.get("currency", "BRL"),
        "period_months": plan.get("period_months", 1),
        "max_uploads_per_month": plan.get("max_uploads_per_month", 1),
        "features": plan.get("features", []),
        "active": plan.get("active", True),
    }

def plans_entity(plans) -> list:
    return [plan_entity(p) for p in plans]

def user_entity(user) -> dict:
    return {
        "id": str(user.get("_id")),
        "name": user.get("name"),
        "email": user.get("email"),
        "whatsapp": user.get("whatsapp"),
        "status": user.get("status", "active"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
        "usage": user.get("usage", {}),
        "subscription": user.get("subscription", {}),
    }

def users_entity(users) -> list:
    return [user_entity(u) for u in users]

# -------------------------------
# 🔹 Pydantic Models
# -------------------------------
class PlanModel(BaseModel):
    code: str                     # ex: "free", "premium"
    name: str                     # ex: "Grátis", "Premium"
    price: float = 0.0
    currency: str = "BRL"
    period_months: int = 1
    max_uploads_per_month: int = 1
    features: List[str] = []
    active: bool = True

class SubscriptionModel(BaseModel):
    plan_id: str
    plan_code: str
    plan_name: str
    active: bool = True
    start_date: datetime
    end_date: datetime
    renewal_day: int
    last_renewal: Optional[datetime] = None
    next_renewal: Optional[datetime] = None

class UserModel(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = "Usuário WhatsApp"
    email: Optional[EmailStr] = None
    whatsapp: str = Field(..., description="E.164 sem + ex: 5511999999999")
    status: str = "active"        # active | blocked | deleted
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    usage: Dict[str, Any] = {}
    subscription: Optional[Dict[str, Any]] = None
