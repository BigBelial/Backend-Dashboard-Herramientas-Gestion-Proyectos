from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from infrastructure.config.settings import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    await mongodb.db.command("ping")
    await _create_indexes()


async def _create_indexes() -> None:
    db = mongodb.db
    await db["users"].create_index("email", unique=True)
    # TTL index: MongoDB auto-removes expired blacklisted tokens
    await db["token_blacklist"].create_index("expires_at", expireAfterSeconds=0)
    await db["token_blacklist"].create_index("jti", unique=True)


async def close_mongo_connection() -> None:
    if mongodb.client:
        mongodb.client.close()


def get_database() -> AsyncIOMotorDatabase:
    return mongodb.db
