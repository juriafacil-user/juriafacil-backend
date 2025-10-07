from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.routes.auth import get_password_hash, get_current_user

router = APIRouter()


@router.post("/users/")
async def create_user(user: dict):
    existing_user = await db["users"].find_one({"email": user["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    user["password"] = get_password_hash(user["password"])
    await db["users"].insert_one(user)
    return {"message": "Usuário criado com sucesso!"}


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "name": current_user["name"]}
