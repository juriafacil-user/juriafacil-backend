from fastapi import APIRouter, HTTPException
from app.database import db
from app.models import user_entity, users_entity
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import Optional, List

router = APIRouter(prefix="/users", tags=["Users"])

# Schemas dentro do próprio arquivo (pode separar se quiser)
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str

collection = db["users"]

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    result = await collection.insert_one(user.dict())
    new_user = await collection.find_one({"_id": result.inserted_id})
    return user_entity(new_user)

@router.get("/", response_model=List[UserResponse])
async def list_users():
    users = await collection.find().to_list(100)
    return users_entity(users)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user_entity(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    if update_data:
        await collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = await collection.find_one({"_id": ObjectId(user_id)})
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user_entity(updated_user)

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    result = await collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário deletado com sucesso"}
