from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from url_shortener.config.settings import settings
import logging

class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

mongoDB = MongoDB()

async def connect_to_mongo():
    try:
        mongoDB.client = AsyncIOMotorClient(settings.mongodb_url)
        mongoDB.database = mongoDB.client[settings.database_name]

        await mongoDB.client.admin.command('ping')
        logging.info("Connected to MongoDB Successfully")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    if mongoDB.client:
        mongoDB.client.close()
        logging.info("Closing MongoDB Successfully")

async def get_database() -> AsyncIOMotorDatabase:
    return mongoDB.database
