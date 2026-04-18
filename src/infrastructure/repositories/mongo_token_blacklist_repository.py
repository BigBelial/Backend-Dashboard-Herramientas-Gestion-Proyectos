from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.repositories.token_blacklist_repository import TokenBlacklistRepository


class MongoTokenBlacklistRepository(TokenBlacklistRepository):
    COLLECTION = "token_blacklist"

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[self.COLLECTION]

    async def add(self, jti: str, expires_at: datetime) -> None:
        await self._col.update_one(
            {"jti": jti},
            {"$setOnInsert": {"jti": jti, "expires_at": expires_at}},
            upsert=True,
        )

    async def is_blacklisted(self, jti: str) -> bool:
        doc = await self._col.find_one({"jti": jti})
        return doc is not None
