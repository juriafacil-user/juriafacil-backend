from fastapi import FastAPI
from app.routes import users, auth, whatsapp, billing
from app.webhooks.mercadopago import router as mercadopago_router

app = FastAPI(title="API JuriFacil 🚀")

# Registrar rotas
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(whatsapp.router)
app.include_router(billing.router)
app.include_router(mercadopago_router, tags=["MercadoPago"])

@app.get("/")
def root():
    return {"message": "API JuriaFacil funcionando 🚀"}

