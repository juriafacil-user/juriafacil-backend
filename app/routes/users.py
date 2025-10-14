from fastapi import APIRouter, HTTPException, status, Depends, Query
from bson import ObjectId
from datetime import datetime
from app.utils.database import db
from app.utils.user_helper import get_or_create_user
from app.models import user_entity, users_entity, UserModel
from app.schemas import UserCreateWhatsApp, UserUpdate
from typing import Optional

router = APIRouter(prefix="/users", tags=["Users"])

# 🟩 Listar todos os usuários (paginação simples)
@router.get("/")
async def get_users(limit: int = Query(100, le=500), skip: int = 0):
    users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    return {"users": users_entity(users)}

# 🟩 Buscar por WhatsApp
@router.get("/by-whatsapp/{whatsapp}")
async def get_user_by_whatsapp(whatsapp: str):
    user = await db.users.find_one({"whatsapp": whatsapp})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user": user_entity(user)}

# 🟨 Criar usuário (WhatsApp-first)
@router.post("/", status_code=201)
async def create_user(data: UserCreateWhatsApp):
    # normaliza whatsapp (apenas dígitos)
    whatsapp = "".join(c for c in data.whatsapp if c.isdigit())
    exists = await db.users.find_one({"whatsapp": whatsapp})
    if exists:
        raise HTTPException(status_code=409, detail="WhatsApp já cadastrado")

    # usa helper para criar já com plano free
    new_user = await get_or_create_user(whatsapp_number=whatsapp, name=data.name or "Usuário WhatsApp")
    return {"user": user_entity(new_user)}

# 🟧 Atualizar dados básicos
@router.patch("/{id}")
async def update_user(id: str, data: UserUpdate):
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")

    updates = {k: v for k, v in data.dict().items() if v is not None}
    updates["updated_at"] = datetime.utcnow().isoformat()
    result = await db.users.update_one({"_id": oid}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user = await db.users.find_one({"_id": oid})
    return {"user": user_entity(user)}

# 🟥 Buscar por ID
@router.get("/{id}")
async def get_user(id: str):
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    user = await db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user": user_entity(user)}
