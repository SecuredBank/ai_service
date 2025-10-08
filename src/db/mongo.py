"""
MongoDB connection and database operations for AI Secured Bank.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    sync_client = None

db = MongoDB()

async def create_indexes():
    """Create necessary indexes for the database."""
    try:
        # Users collection indexes
        user_indexes = [
            IndexModel([("username", ASCENDING)], unique=True, name="username_unique"),
            IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
            IndexModel([("role", ASCENDING)], name="role_index"),
            IndexModel([("isEmailVerified", ASCENDING)], name="email_verified_index"),
            IndexModel([("isKycVerified", ASCENDING)], name="kyc_verified_index"),
            IndexModel([("createdAt", DESCENDING)], name="created_at_desc"),
            IndexModel([("updatedAt", DESCENDING)], name="updated_at_desc")
        ]
        
        # KYC collection indexes
        kyc_indexes = [
            IndexModel([("user", ASCENDING)], unique=True, name="user_unique"),
            IndexModel([("status", ASCENDING)], name="status_index"),
            IndexModel([("documentNumber", ASCENDING)], unique=True, sparse=True, name="document_number_unique"),
            IndexModel([("isVerified", ASCENDING)], name="is_verified_index"),
            IndexModel([("createdAt", DESCENDING)], name="kyc_created_at_desc"),
            IndexModel([("updatedAt", DESCENDING)], name="kyc_updated_at_desc")
        ]
        
        # Create indexes
        await db.db.users.create_indexes(user_indexes)
        await db.db.kyc.create_indexes(kyc_indexes)
        
        logger.info("Database indexes created/verified")
        
    except OperationFailure as e:
        logger.error(f"Error creating indexes: {e}")
        raise

async def connect_to_mongo():
    """Connect to MongoDB and set up the database."""
    try:
        # Connect to MongoDB
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.sync_client = MongoClient(settings.mongodb_url)
        db.db = db.client[settings.mongodb_db_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
        # Create admin user if it doesn't exist
        await create_default_admin()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_default_admin():
    """Create a default admin user if no admin exists."""
    from services.auth_services import AuthService
    
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@securedbank.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123")
    
    try:
        # Check if admin exists
        existing_admin = await db.db.users.find_one({"email": admin_email, "role": "ADMIN"})
        
        if not existing_admin:
            # Create admin user
            admin_data = {
                "fullnames": "System Administrator",
                "username": "admin",
                "email": admin_email,
                "password": AuthService.get_password_hash(admin_password),
                "role": "ADMIN",
                "isEmailVerified": True,
                "isKycVerified": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            await db.db.users.insert_one(admin_data)
            logger.info("Default admin user created")
            
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        # Don't raise the exception to allow the app to start

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client is not None:
        await db.client.close()
        db.sync_client.close()
        logger.info("MongoDB connection closed")
