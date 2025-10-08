from fastapi import APIRouter, Request, HTTPException
import httpx
import os
from app.utils.database import db  # conexão MongoDB

router = APIRouter()

# =============================
# ⚙️ CONFIGURAÇÃO MERCADO PAGO
# =============================
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
WEBHOOK_SECRET = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")

if not MERCADO_PAGO_ACCESS_TOKEN:
    print("⚠️ AVISO: MERCADOPAGO_ACCESS_TOKEN não configurado. O módulo de pagamento não funcionará.")


@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    # 🔒 Validação opcional da assinatura secreta
    if WEBHOOK_SECRET:
        signature = request.headers.get("x-signature")
        if signature != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Assinatura inválida")

    body = await request.json()
    print("📩 Webhook recebido:", body)

    # ✅ Extrai o ID do pagamento
    payment_id = body.get("data", {}).get("id")
    if not payment_id:
        return {"status": "ignored", "reason": "no payment id"}

    # 🔍 Busca detalhes do pagamento via API do Mercado Pago
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        )

    payment_data = response.json()
    print("🔍 Dados do pagamento:", payment_data)

    # 💳 Se o pagamento foi aprovado
    if payment_data.get("status") == "approved":
        payer_email = payment_data["payer"].get("email")

        if not payer_email:
            return {"status": "ignored", "reason": "no payer email"}

        # 🚀 Chama internamente o endpoint de upgrade
        async with httpx.AsyncClient() as client:
            upgrade_resp = await client.post(
                "https://juriafacil.onrender.com/billing/upgrade",
                json={"email": payer_email}
            )

        print("📤 Resposta do upgrade:", upgrade_resp.text)
        return {"status": "success", "email": payer_email}

    return {"status": "ok", "reason": "payment not approved"}
