from fastapi import FastAPI
from app.routes import users, auth, whatsapp

app = FastAPI(title="API JuriFacil 🚀")

# Registrar rotas
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(whatsapp.router)
app.include_router(billing.router)

@app.get("/")
def root():
    return {"message": "API JuriaFacil funcionando 🚀"}

