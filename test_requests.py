import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_user():
    data = {
        "name": "Teste Usuário",
        "email": "teste@teste.com",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/users/", json=data)
    print("Create User:", response.status_code, response.json())
    return response.json()["id"]

def test_list_users():
    response = requests.get(f"{BASE_URL}/users/")
    print("List Users:", response.status_code, response.json())

def test_get_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print("Get User:", response.status_code, response.json())

def test_update_user(user_id):
    data = {"name": "Usuário Atualizado"}
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=data)
    print("Update User:", response.status_code, response.json())

def test_delete_user(user_id):
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    print("Delete User:", response.status_code, response.json())

if __name__ == "__main__":
    user_id = test_create_user()
    test_list_users()
    test_get_user(user_id)
    test_update_user(user_id)
    test_delete_user(user_id)
    test_list_users()
