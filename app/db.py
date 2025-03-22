from http.client import HTTPException
import logging
import motor.motor_asyncio
from fastapi import FastAPI, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

MONGO_URI = "mongodb://admin:adminpassword@192.168.117.3:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+2.4.0"
DATABASE_NAME = "logs_db"


client = None
db = None

try:
    client = AsyncIOMotorClient(MONGO_URI)
    # client = MongoClient(MONGO_URI)
    db = client["logs_db"]
    print("MongoDB connection established!")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise HTTPException(status_code=500, detail="Database connection error")