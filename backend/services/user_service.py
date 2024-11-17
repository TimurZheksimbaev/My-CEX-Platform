import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database.connect import get_db
from ..models.user import User
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..repostories.user_repository import UserRepository
from ..schemas.user import UserCreate, Token
from dotenv import load_dotenv

load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> dict[str, str]:
        db_user = await UserRepository.get_user_by_email(db, user_data.email)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = await UserRepository.create_user(db, user_data)
        return {"message": "User successfully registered"}

    @staticmethod
    async def login_user(db: AsyncSession, user_data: UserCreate) -> Token:
        user = await UserRepository.get_user_by_email(db, user_data.email)
        if not user or not await UserRepository.verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
        access_token = await AuthService.create_access_token({"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            user = await UserRepository.get_user_by_email(db, email)
            return user
        except JWTError:
            raise credentials_exception
    @staticmethod
    async def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)




