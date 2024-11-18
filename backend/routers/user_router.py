from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, Token
from database.connect import get_db
from services.user_service import AuthService

router = APIRouter()

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
async def login_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_user(db, user_data)

