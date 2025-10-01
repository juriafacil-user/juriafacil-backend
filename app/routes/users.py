from fastapi import APIRouter
from app.database import db

router = APIRouter()

@router.get("/")
def list_users():
    try:
        users = list(db.users.find({}, {"_id": 0}))
        return {"users": users}
    except Exception as e:
        return {"error": str(e)}

