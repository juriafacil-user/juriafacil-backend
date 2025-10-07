from fastapi import APIRouter, Request
from datetime import datetime
from app.utils.user_helper import get_or_create_user

router = APIRouter()

@router.post("/webhook/whatsapp")
async def receive_whatsapp_message(request: Request):
    """
    Endpoint chamado toda vez que o usuário envia mensagem ou arquivo via WhatsApp.
    Ele cria automaticamente o usuário se for o primeiro contato.
    """
    data = await request.json()

    whatsapp_number = data.get("from")  # Exemplo: "5511999999999"
    user_name = data.get("profile", {}).get("name", "Usuário WhatsApp")
    message_type = data.get("type", "text")

    # ✅ Cria ou busca usuário automaticamente
    user = await get_or_create_user(whatsapp_number, name=user_name)

    plan = user.get("plan", {})
    if not plan.get("active"):
        return {"reply": "Sua assinatura está inativa. Renove para continuar."}

    end_date = datetime.fromisoformat(plan["end_date"])
    if datetime.utcnow() > end_date:
        return {"reply": "⚠️ Seu plano expirou. Renove sua assinatura para continuar."}

    if plan["type"] == "free" and plan["uploads_this_month"] >= plan["max_uploads"]:
        return {"reply": "Você já usou seu upload gratuito deste mês. Assine para continuar usando o JuriFácil."}

    if message_type == "document":
        file_name = data["document"]["filename"]
        plan["uploads_this_month"] += 1
        await request.app.state.db["users"].update_one(
            {"whatsapp": whatsapp_number},
            {"$set": {"plan": plan}}
        )
        return {"reply": f"📄 Documento '{file_name}' recebido! Estamos analisando seu contrato..."}

    message_text = data.get("text", {}).get("body", "").lower()
    if "ajuda" in message_text:
        return {"reply": "Envie um documento para análise ou digite 'planos' para saber mais sobre as assinaturas."}

    return {"reply": "Olá! Envie o contrato que deseja analisar 📑"}

