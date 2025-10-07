import requests

BASE_URL = "https://juriafacil-backend.onrender.com/"

# 1️⃣ Criar usuário
user_data = {
    "name": "Edu Ribeiro",
    "email": "edu@teste.com",
    "password": "123456"
}
print(requests.post(f"{BASE_URL}/users/", json=user_data).json())

# 2️⃣ Consultar plano
print(requests.get(f"{BASE_URL}/billing/check-plan", headers={
    "Authorization": "Bearer TOKEN_JWT"
}).json())

