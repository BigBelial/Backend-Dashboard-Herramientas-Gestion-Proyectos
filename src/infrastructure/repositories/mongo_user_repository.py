from datetime import datetime
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.entities.role import Role
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class MongoUserRepository(UserRepository):
    COLLECTION = "users"

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[self.COLLECTION]

    async def find_by_email(self, email: str) -> Optional[User]:
        doc = await self._col.find_one({"email": email})
        return self._to_entity(doc) if doc else None

    async def find_by_id(self, user_id: str) -> Optional[User]:
        oid = self._to_oid(user_id)
        if not oid:
            return None
        doc = await self._col.find_one({"_id": oid})
        return self._to_entity(doc) if doc else None

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        cursor = self._col.find({}).skip(skip).limit(limit)
        return [self._to_entity(doc) async for doc in cursor]

    async def save(self, user: User) -> User:
        doc = self._to_doc(user)
        result = await self._col.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    async def update(self, user: User) -> User:
        oid = self._to_oid(user.id)
        if not oid:
            return user
        await self._col.update_one(
            {"_id": oid},
            {"$set": {
                "email": user.email,
                "hashed_password": user.hashed_password,
                "is_active": user.is_active,
                "role": user.role.value,
                "updated_at": user.updated_at,
            }},
        )
        return user

    async def delete(self, user_id: str) -> bool:
        oid = self._to_oid(user_id)
        if not oid:
            return False
        result = await self._col.delete_one({"_id": oid})
        return result.deleted_count > 0

    @staticmethod
    def _to_oid(user_id: str) -> Optional[ObjectId]:
        try:
            return ObjectId(user_id)
        except Exception:
            return None

    @staticmethod
    def _to_doc(user: User) -> dict:
        return {
            "email": user.email,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active,
            "role": user.role.value,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def _to_entity(doc: dict) -> User:
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            is_active=doc.get("is_active", True),
            role=Role(doc.get("role", Role.CONSULTOR.value)),
            created_at=doc.get("created_at", datetime.utcnow()),
            updated_at=doc.get("updated_at", datetime.utcnow()),
        )
