from fastapi import APIRouter, Request
from datetime import datetime
from app.utils.user_helper import get_or_create_user
from app.utils.database import db

router = APIRouter()

@router.post("/webhook/whatsapp")
async def receive_whatsapp_message(request: Request):
    """Cria/garante usuário por WhatsApp e responde comandos básicos."""
    data = await request.json()
    whatsapp_number = data.get("from")  # Ex.: "5511999999999"
    user_name = data.get("profile", {}).get("name", "Usuário WhatsApp")

    user = await get_or_create_user(whatsapp_number=whatsapp_number, name=user_name)

    # Se for documento (mock existente)
    if data.get("type") == "document":
        file_name = data["document"]["filename"]
        # incrementa uso do mês
        await db.users.update_one({"whatsapp": user["whatsapp"]}, {"$inc": {"usage.uploads_this_month": 1, "usage.uploads_total": 1}})
        return {"reply": f"📄 Documento '{file_name}' recebido! Estamos analisando seu contrato..."}

    # Comandos de texto
    message_text = (data.get("text", {}) or {}).get("body", "").lower()
    if "planos" in message_text:
        plans = await db.plans.find({"active": True}).to_list(20)
        names = ", ".join([p.get("name") for p in plans]) or "Free"
        return {"reply": f"Planos disponíveis: {names}. Envie 'assinar premium' para assinar."}

    if "assinar" in message_text and "premium" in message_text:
        return {"reply": "Perfeito! Acesse o link para assinar: /billing/checkout?plan_code=premium&whatsapp=" + user["whatsapp"]}

    if "ajuda" in message_text:
        return {"reply": "Envie um documento para análise ou digite 'planos' para saber mais sobre as assinaturas."}

    return {"reply": "Olá! Envie o contrato que deseja analisar 📑"}
