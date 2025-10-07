from datetime import datetime, timedelta
from app.database import db

async def get_or_create_user(whatsapp_number: str, name: str = None):
    """
    Busca usuário pelo número do WhatsApp.
    Se não existir, cria automaticamente com plano free.
    """
    user = await db["users"].find_one({"whatsapp": whatsapp_number})

    if not user:
        new_user = {
            "name": name or "Usuário WhatsApp",
            "email": None,
            "whatsapp": whatsapp_number,
            "password": None,  # não precisa senha para uso via WhatsApp
            "plan": {
                "type": "free",
                "active": True,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "uploads_this_month": 0,
                "max_uploads": 1
            },
            "created_at": datetime.utcnow().isoformat()
        }
        await db["users"].insert_one(new_user)
        return new_user

    return user
