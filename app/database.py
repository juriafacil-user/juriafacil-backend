from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGO_URL)
db = client["juriafacil"]  # nome do banco
