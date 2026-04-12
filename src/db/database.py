from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.database import Database

from src.lib.utils.config import APP_NAME, MONGO_URL

    
async def get_db() -> Database:
    """Get async MongoDB database instance with configured indexes.

    Creates indexes for:
    - users: email (unique)
    - roles: title (unique), description
    - notifications: subject
    - transactions: item, description, category, vendor
    - receipts: vendor, notes

    Returns:
        AsyncIOMotorClient database instance
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db: Database = client[APP_NAME]

    db.users.create_index([('email', 1)], unique=True)

    db.roles.create_index([('title', 1)], unique=True)
    db.roles.create_index([('description', 1)])

    db.notification.create_index([('subject', 1)])

    db.simulations.create_index([('author_id', 1)])
    db.simulation_transactions.create_index([('holder', 1), ('holder_bank', 1), ('reference', 1)])
    db.simulation_profiles.create_index([('user_id', 1), ('user_name', 1), ('name', 1), ('email', 1)])
    db.simulation_devices.create_index([('owner', 1), ('device_id', 1)])
    db.simulation_accounts.create_index([('account_no', 1), ('bank_name', 1), ('account_name', 1)])

    return db


def get_db_sync() -> Database:
    """Get synchronous MongoDB database instance.

    Returns:
        MongoClient database instance
    """
    client = MongoClient(MONGO_URL)
    db: Database = client[APP_NAME]
    return db