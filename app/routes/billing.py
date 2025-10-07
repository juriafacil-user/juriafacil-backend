from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.utils.database import db
from app.utils.user_helper import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing"])

FREE_UPLOAD_LIMIT = 1  # limite de 1 upload gratuito

@router.get("/check-plan")
async def check_plan(user: dict = Depends(get_current_user)):
    user_data = await db.users.find_one({"email": user["email"]})
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Se for plano gratuito e já usou o upload gratuito
    if user_data["plan"] == "free" and user_data["upload_count"] >= FREE_UPLOAD_LIMIT:
        return {
            "status": "limit_reached",
            "message": "Você já utilizou seu upload gratuito. Faça upgrade para o plano Premium."
        }

    return {
        "status": "ok",
        "plan": user_data["plan"],
        "uploads": user_data["upload_count"]
    }

@router.post("/register-upload")
async def register_upload(user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"email": user["email"]},
        {"$inc": {"upload_count": 1}, "$set": {"last_upload": datetime.utcnow()}}
    )
    return {"message": "Upload registrado com sucesso"}

@router.post("/upgrade")
async def upgrade_to_premium(user: dict = Depends(get_current_user)):
    new_expiration = datetime.utcnow() + timedelta(days=30)
    await db.users.update_one(
        {"email": user["email"]},
        {"$set": {"plan": "premium", "plan_expiration": new_expiration}}
    )
    return {
        "message": "Plano Premium ativado com sucesso!",
        "expires_in": new_expiration
    }
