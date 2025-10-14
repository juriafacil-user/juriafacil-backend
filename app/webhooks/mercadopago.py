from fastapi import APIRouter, Request, HTTPException
import httpx
import os
from datetime import datetime, timedelta
from app.utils.database import db  # conexão MongoDB

router = APIRouter()

MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not MERCADO_PAGO_ACCESS_TOKEN:
    print("⚠️ AVISO: MERCADOPAGO_ACCESS_TOKEN não configurado. O módulo de pagamento não funcionará.")

@router.post("/mercadopago")
async def mercadopago_webhook(request: Request):
    body = await request.json()
    print("📩 Webhook recebido:", body)

    payment_id = body.get("data", {}).get("id")
    if not payment_id:
        return {"status": "ignored", "reason": "no payment id"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        )

    payment_data = response.json()
    print("🔍 Dados do pagamento:", payment_data)

    if payment_data.get("status") != "approved":
        return {"status": "ok", "reason": "payment not approved"}

    metadata = payment_data.get("metadata", {}) or {}
    whatsapp = metadata.get("whatsapp")
    plan_code = metadata.get("plan_code", "premium")

    if not whatsapp:
        print("⚠️ Nenhum WhatsApp encontrado no pagamento.")
        return {"status": "ignored", "reason": "no whatsapp metadata"}

    user = await db.users.find_one({"whatsapp": "".join(c for c in whatsapp if c.isdigit())})
    if not user:
        print("⚠️ Usuário não encontrado para upgrade.")
        return {"status": "ignored", "reason": "user not found"}

    plan = await db.plans.find_one({"code": plan_code, "active": True})
    if not plan:
        print("⚠️ Plano não encontrado para upgrade.")
        return {"status": "ignored", "reason": "plan not found"}

    start = datetime.utcnow()
    end = start + timedelta(days=30 * plan.get("period_months", 1))
    subscription = {
        "plan_id": str(plan["_id"]),
        "plan_code": plan["code"],
        "plan_name": plan["name"],
        "active": True,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "renewal_day": start.day,
        "last_renewal": start.isoformat(),
        "next_renewal": end.isoformat(),
    }
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"subscription": subscription}})
    print(f"✅ Upgrade feito para {whatsapp} ({plan_code})")
    return {"status": "success", "whatsapp": whatsapp, "plan_code": plan_code}
