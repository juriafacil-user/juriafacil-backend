from fastapi import APIRouter, Request
import httpx
import os
import mercadopago
from app.utils.database import db  # conexão MongoDB

router = APIRouter()

# =============================
# ⚙️ CONFIGURAÇÃO MERCADO PAGO
# =============================
token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not token:
    print("⚠️ AVISO: MERCADOPAGO_ACCESS_TOKEN não configurado. O módulo de pagamento não funcionará.")
    token = "SEM_TOKEN"

MERCADO_PAGO_ACCESS_TOKEN = mercadopago.SDK(str(token))

signature = request.headers.get("x-signature")
if signature != os.getenv("MERCADOPAGO_WEBHOOK_SECRET"):
    return {"status": "unauthorized"} 

@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    body = await request.json()
    print("📩 Webhook recebido:", body)

    # Verifica se veio o ID do pagamento
    payment_id = None
    if "data" in body and "id" in body["data"]:
        payment_id = body["data"]["id"]
    else:
        return {"status": "ignored", "reason": "no payment id"}

    # Busca informações completas do pagamento
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        )

    payment_data = response.json()
    print("🔍 Dados do pagamento:", payment_data)

    if payment_data.get("status") == "approved":
        payer_email = payment_data["payer"].get("email")

        # Atualiza o plano no banco
        result = await db["users"].update_one(
            {"email": payer_email},
            {"$set": {"plano": "premium"}}
        )

        if result.modified_count > 0:
            print(f"✅ Plano premium ativado para {payer_email}")
        else:
            print(f"⚠️ Usuário não encontrado: {payer_email}")

    return {"status": "ok"}

