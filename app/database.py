from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["juriafacil"]  # nome do banco
