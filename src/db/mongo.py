"""
MongoDB connection and database operations.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import os
from dotenv import load_dotenv
from core.config import get_settings

load_dotenv()
settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    sync_client = None

db = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB."""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.sync_client = MongoClient(settings.mongodb_url)
        db.db = db.client[settings.mongodb_db_name]
        # Test the connection
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client is not None:
        db.client.close()
        db.sync_client.close()
        print("MongoDB connection closed")
