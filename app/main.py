from fastapi import FastAPI
from app.routes import users, auth, whatsapp, billing
from app.webhooks import mercadopago
from app.utils.database import ensure_indexes, db

app = FastAPI(title="API JuriFacil 🚀")

@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    # Seed básico de planos se vazio
    count = await db.plans.count_documents({})
    if count == 0:
        await db.plans.insert_many([
            {
                "code": "free",
                "name": "Grátis",
                "price": 0.0,
                "currency": "BRL",
                "period_months": 1,
                "max_uploads_per_month": 1,
                "features": ["1 upload/mês", "Resumo básico"],
                "active": True,
            },
            {
                "code": "premium",
                "name": "Premium",
                "price": 9.90,
                "currency": "BRL",
                "period_months": 1,
                "max_uploads_per_month": 30,
                "features": ["Até 30 uploads/mês", "Resumo avançado", "Fila prioritária"],
                "active": True,
            }
        ])

# Registrar rotas
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(whatsapp.router)
app.include_router(billing.router)
app.include_router(mercadopago.router, prefix="/webhook", tags=["MercadoPago"])

@app.get("/")
def root():
    return {"message": "API JuriaFacil funcionando 🚀"}
