from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["juriafacil"]  # nome do banco
