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
sdk = mercadopago.SDK(token) if token else None

# 🔹 Listar planos ativos
@router.get("/plans")
async def list_plans():
    plans = await db.plans.find({"active": True}).to_list(100)
    return {"plans": [{
        "id": str(p["_id"]),
        "code": p["code"],
        "name": p["name"],
        "price": p["price"],
        "currency": p.get("currency", "BRL"),
        "period_months": p.get("period_months", 1),
        "max_uploads_per_month": p.get("max_uploads_per_month", 1),
        "features": p.get("features", []),
        "active": p.get("active", True),
    } for p in plans]}

# 🔹 Criar preferência de pagamento (inclui whatsapp nos metadados)
@router.post("/checkout")
async def create_checkout(whatsapp: str = Query(...), plan_code: str = Query("premium")):
    if not sdk:
        raise HTTPException(status_code=500, detail="Mercado Pago não configurado")
    user = await get_or_create_user(whatsapp_number=whatsapp)

    plan = await db.plans.find_one({"code": plan_code, "active": True})
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    price = float(plan.get("price", 0))
    title = f"Assinatura {plan.get('name','Plano')} JuriFácil"

    preference_data = {
        "items": [{"title": title, "quantity": 1, "unit_price": price}],
        "metadata": {"whatsapp": user["whatsapp"], "plan_code": plan_code},
        "payer": {"first_name": user.get("name") or "Usuário WhatsApp"},
        "back_urls": {
            "success": os.getenv("CHECKOUT_SUCCESS_URL", "https://juriafacil.com/sucesso"),
            "failure": os.getenv("CHECKOUT_FAILURE_URL", "https://juriafacil.com/erro"),
            "pending": os.getenv("CHECKOUT_PENDING_URL", "https://juriafacil.com/pendente"),
        },
        "auto_return": "approved",
    }
    preference_response = sdk.preference().create(preference_data)
    response = preference_response["response"]
    init_point = response.get("init_point", "")
    if "TEST-" in (os.getenv("MERCADOPAGO_ACCESS_TOKEN") or "") and "sandbox." not in init_point:
        init_point = init_point.replace("https://www.mercadopago.com.br/", "https://sandbox.mercadopago.com.br/")
    return {"init_point": init_point}

# 🔹 Upgrade de plano manual (ex: fallback do webhook)
@router.post("/upgrade")
async def upgrade(whatsapp: str = Query(...), plan_code: str = Query("premium")):
    user = await db.users.find_one({"whatsapp": "".join(c for c in whatsapp if c.isdigit())})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    plan = await db.plans.find_one({"code": plan_code, "active": True})
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

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
    return {"status": "ok", "subscription": subscription}
