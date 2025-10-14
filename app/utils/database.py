from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGODB_URI)
db = client["juriafacil"]  # nome do banco

async def ensure_indexes():
    # Users: whatsapp único e índice na assinatura
    await db.users.create_index("whatsapp", unique=True, name="uniq_whatsapp")
    await db.users.create_index("subscription.plan_id", name="idx_subscription_plan")
    await db.users.create_index("subscription.active", name="idx_subscription_active")
    await db.users.create_index("created_at", name="idx_created_at")
    # Plans: code único e ativos
    await db.plans.create_index("code", unique=True, name="uniq_plan_code")
    await db.plans.create_index("active", name="idx_plan_active")
