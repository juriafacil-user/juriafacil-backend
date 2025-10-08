from fastapi import APIRouter, HTTPException, Query, Request
from datetime import datetime, timedelta
from app.utils.database import db
from app.utils.user_helper import get_or_create_user
import mercadopago
import os
import json

router = APIRouter(prefix="/billing", tags=["Billing"])

# =============================
# ⚙️ CONFIGURAÇÃO MERCADO PAGO
# =============================
token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not token:
    print("⚠️ AVISO: MERCADOPAGO_ACCESS_TOKEN não configurado. O módulo de pagamento não funcionará.")
    token = "SEM_TOKEN"

sdk = mercadopago.SDK(str(token))


FREE_UPLOAD_LIMIT = 1  # limite de 1 upload gratuito

# =============================
# 🔹 1. Verificar plano
# =============================
@router.get("/check-plan")
async def check_plan(whatsapp: str = Query(...)):
    """
    Verifica o plano atual do usuário pelo número do WhatsApp.
    Se o usuário não existir, ele é criado automaticamente.
    """
    user = await get_or_create_user(whatsapp)
    plan = user.get("plan", {})

    uploads = plan.get("uploads_this_month", 0)
    limit = plan.get("max_uploads", FREE_UPLOAD_LIMIT)
    plan_type = plan.get("type", "free")

    if plan_type == "free" and uploads >= limit:
        return {
            "status": "limit_reached",
            "message": "Você já utilizou seu upload gratuito. Faça upgrade para o plano Premium."
        }

    return {
        "status": "ok",
        "plan": plan_type,
        "uploads": uploads,
        "limit": limit
    }

# =============================
# 🔹 2. Registrar upload
# =============================
@router.post("/register-upload")
async def register_upload(whatsapp: str = Query(...)):
    """
    Incrementa o número de uploads feitos no mês.
    """
    user = await get_or_create_user(whatsapp)
    plan = user.get("plan", {})

    new_uploads = plan.get("uploads_this_month", 0) + 1

    await db["users"].update_one(
        {"whatsapp": whatsapp},
        {"$set": {"plan.uploads_this_month": new_uploads}}
    )

    return {
        "message": "Upload registrado com sucesso",
        "uploads": new_uploads
    }

# =============================
# 🔹 3. Upgrade manual / webhook
# =============================
@router.post("/upgrade")
async def upgrade_to_premium(whatsapp: str = Query(...)):
    """
    Atualiza o plano para Premium (manual ou via callback do Mercado Pago).
    """
    new_plan = {
        "type": "premium",
        "active": True,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "uploads_this_month": 0,
        "max_uploads": 999
    }

    result = await db["users"].update_one(
        {"whatsapp": whatsapp},
        {"$set": {"plan": new_plan}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {"message": "Plano Premium ativado com sucesso!", "plan": new_plan}

# =============================
# 🔹 4. Criar link de assinatura Mercado Pago
# =============================
@router.post("/create-subscription")
async def create_subscription(whatsapp: str = Query(...)):
    """
    Cria o link de pagamento da assinatura Premium.
    """
    user = await get_or_create_user(whatsapp)
    
    preference_data = {
        "items": [
            {
                "title": "Assinatura JuriFácil Premium",
                "quantity": 1,
                "unit_price": 29.90
            }
        ],
        "payer": {
            "name": user["name"],
            "email": user.get("email") or "sememail@juriafacil.com",
        },
        "metadata": {
            "whatsapp": whatsapp
        },
        "back_urls": {
            "success": "https://juriafacil.com/sucesso",
            "failure": "https://juriafacil.com/erro",
            "pending": "https://juriafacil.com/pendente"
        },
        "auto_return": "approved"
    }
    
 
    
    preference_response = sdk.preference().create(preference_data)
    # return {"init_point": preference_response["response"]["init_point"]}
    response = preference_response["response"]
    
    # 🔍 Ajusta o link para sandbox, se estiver usando token de teste
    init_point = response.get("init_point", "")
    if "TEST-" in token and "sandbox." not in init_point:
        init_point = init_point.replace(
            "https://www.mercadopago.com.br/",
            "https://sandbox.mercadopago.com.br/"
        )
    
    return {"init_point": init_point}

# =============================
# 🔹 5. Cirar Rota do webhook
# =============================
@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)
        print("🔔 Webhook recebido:", data)
        return {"status": "received"}
    except Exception as e:
        print("Erro no webhook:", e)
        return {"error": str(e)}
