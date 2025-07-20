# app/db/connection.py
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI not found in .env")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["ecommerce"]  # use your DB name here
