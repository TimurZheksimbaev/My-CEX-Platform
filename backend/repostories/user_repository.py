from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User
from ..schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, userCreate: UserCreate) -> User:
        hashed_password = pwd_context.hash(userCreate.password)
        user = User(email=userCreate.email, hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        query = select(User).filter(User.id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
