from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreateWhatsApp(BaseModel):
    whatsapp: str
    name: Optional[str] = "Usuário WhatsApp"
    email: Optional[EmailStr] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None

class PlanCreate(BaseModel):
    code: str
    name: str
    price: float = 0.0
    currency: str = "BRL"
    period_months: int = 1
    max_uploads_per_month: int = 1
    features: List[str] = []
    active: bool = True
