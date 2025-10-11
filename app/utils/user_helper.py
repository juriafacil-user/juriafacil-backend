from datetime import datetime, timedelta
from app.utils.database import db

async def _get_default_plan():
    # tenta pegar plano 'free', senão cria um de fallback
    plan = await db.plans.find_one({"code": "free", "active": True})
    if not plan:
        plan = {
            "code": "free",
            "name": "Grátis",
            "price": 0.0,
            "currency": "BRL",
            "period_months": 1,
            "max_uploads_per_month": 1,
            "features": ["1 upload/mês", "Resumo básico"],
            "active": True,
        }
        res = await db.plans.insert_one(plan)
        plan["_id"] = res.inserted_id
    return plan

def _next_renewal_dates(period_months: int):
    start = datetime.utcnow()
    end = start + timedelta(days=30 * period_months)
    return start, end

async def get_or_create_user(whatsapp_number: str, name: str = None):
    """
    Busca usuário pelo número do WhatsApp.
    Se não existir, cria automaticamente com plano 'free' (vindo da collection plans).
    """
    whatsapp_number = "".join(c for c in whatsapp_number if c.isdigit())
    user = await db.users.find_one({"whatsapp": whatsapp_number})
    if user:
        return user

    plan = await _get_default_plan()
    start, end = _next_renewal_dates(plan.get("period_months", 1))

    new_user = {
        "name": name or "Usuário WhatsApp",
        "email": None,
        "whatsapp": whatsapp_number,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "usage": {"uploads_this_month": 0, "uploads_total": 0},
        "subscription": {
            "plan_id": str(plan["_id"]),
            "plan_code": plan["code"],
            "plan_name": plan["name"],
            "active": True,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "renewal_day": start.day,
            "last_renewal": None,
            "next_renewal": end.isoformat(),
        },
    }
    await db.users.insert_one(new_user)
    return new_user
