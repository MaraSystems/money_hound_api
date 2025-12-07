from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database

from .config import MONGO_URL, MONGO_DB
    
async def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db: Database = client[MONGO_DB]

    db.users.create_index([('email', 1)], unique=True)

    db.roles.create_index([('title', 1)], unique=True)
    db.roles.create_index([('description', 1)])

    db.notification.create_index([('subject', 1)])

    db.simulations.create_index([('author_id', 1)])
    db.simulation_transactions.create_index([('holder', 1), ('holder_bank', 1), ('reference', 1)])
    db.simulation_profiles.create_index([('user_id', 1), ('user_name', 1), ('name', 1), ('email', 1)])
    db.simulation_bank_devices.create_index([('bank_name', 1), ('device_id', 1)])
    db.simulation_accounts.create_index([('account_no', 1), ('bank_name', 1), ('account_name', 1)])


    return db