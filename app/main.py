from fastapi import FastAPI
from app.routes import users

app = FastAPI(title="JuriFacil API")

# Rotas
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "API JuriFacil funcionando 🚀"}
