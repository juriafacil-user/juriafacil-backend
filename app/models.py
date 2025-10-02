from bson import ObjectId

def user_entity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }

def users_entity(users) -> list:
    return [user_entity(user) for user in users]

