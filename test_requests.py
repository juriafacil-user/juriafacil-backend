import requests

BASE_URL = "http://127.0.0.1:8000"

# Criar usuário
user_data = {"name": "Edu Ribeiro", "email": "edu@teste.com", "password": "123456"}
print(requests.post(f"{BASE_URL}/users/", json=user_data).json())

# Login
token = requests.post(
    f"{BASE_URL}/auth/token",
    data={"username": "edu@teste.com", "password": "123456"},
).json()
print(token)

# Rota protegida
headers = {"Authorization": f"Bearer {token['access_token']}"}
print(requests.get(f"{BASE_URL}/users/me", headers=headers).json())
