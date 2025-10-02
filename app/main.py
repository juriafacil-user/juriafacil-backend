from fastapi import FastAPI
from app.routes import users

app = FastAPI(title="API JuriFacil 🚀")

# Registrar rotas
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "API JuriFacil funcionando 🚀"}
