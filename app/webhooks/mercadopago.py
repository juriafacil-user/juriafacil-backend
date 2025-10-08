from fastapi import APIRouter, Request, HTTPException
import httpx
import os
from app.utils.database import db  # conexão MongoDB

router = APIRouter()

MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
WEBHOOK_SECRET = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")

if not MERCADO_PAGO_ACCESS_TOKEN:
    print("⚠️ AVISO: MERCADOPAGO_ACCESS_TOKEN não configurado. O módulo de pagamento não funcionará.")


@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    # 🔒 Validação opcional da assinatura secreta
    #if WEBHOOK_SECRET:
     #   signature = request.headers.get("x-signature")
      #  if signature != WEBHOOK_SECRET:
       #     raise HTTPException(status_code=401, detail="Assinatura inválida")

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

    if payment_data.get("status") == "approved":
        # 🧠 Recupera o WhatsApp enviado nos metadados
        metadata = payment_data.get("metadata", {})
        whatsapp = metadata.get("whatsapp")

        if not whatsapp:
            print("⚠️ Nenhum WhatsApp encontrado no pagamento. Não foi possível fazer upgrade.")
            return {"status": "ignored", "reason": "no whatsapp metadata"}

        # 🚀 Faz o upgrade chamando a rota existente
        async with httpx.AsyncClient() as client:
            upgrade_url = f"https://juriafacil.onrender.com/billing/upgrade?whatsapp={whatsapp}"
            upgrade_resp = await client.post(upgrade_url)

        print(f"✅ Upgrade feito para {whatsapp} - Resposta:", upgrade_resp.text)
        return {"status": "success", "whatsapp": whatsapp}

    return {"status": "ok", "reason": "payment not approved"}
