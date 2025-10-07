from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.database import db
from app.routes.auth import get_password_hash, get_current_user
from app.schemas import UserCreate
from app.models import user_entity, users_entity, UserModel
from bson import ObjectId


router = APIRouter(prefix="/users", tags=["Users"])

# 🟩 Listar todos os usuários
@router.get("/")
async def get_users():
    users = await db.users.find().to_list(100)
    return {"users": users_entity(users)}

# 🟦 Criar novo usuário
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel):
    # Verifica se já existe usuário com o mesmo e-mail
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    new_user = user.dict()
    new_user["plan"] = "free"
    new_user["upload_count"] = 0
    new_user["last_upload"] = None
    new_user["plan_expiration"] = None

    result = await db.users.insert_one(new_user)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return {"user": user_entity(created_user)}

# 🟨 Buscar um usuário específico
@router.get("/{id}")
async def get_user(id: str):
    user = await db.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user": user_entity(user)}


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "name": current_user["name"]}
