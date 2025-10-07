from fastapi import FastAPI
from app.routes import users, auth

app = FastAPI(title="API JuriFacil 🚀")

# Registrar rotas
app.include_router(users.router)
app.include_router(auth.router)

