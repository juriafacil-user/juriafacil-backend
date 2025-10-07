from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.routes.auth import get_password_hash, get_current_user
from app.schemas import UserCreate

router = APIRouter()

@router.get("/users/")
async def list_users():
    return {"message": "Endpoint de usuários ativo ✅"}


@router.post("/users/")
async def create_user(user: UserCreate):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    hashed_password = get_password_hash(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }

    await db["users"].insert_one(new_user)
    return {"message": "Usuário criado com sucesso!"}


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "name": current_user["name"]}
