from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.cex import OrderCreate, OrderResponse, PriceResponse
from ..services.cex_service import CEXService
from ..database.connect import get_db
from ..services.user_service import AuthService
from ..models.user import User

router = APIRouter()

@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str):
    return await CEXService.fetch_crypto_price(symbol)

@router.post("/", response_model=OrderResponse)
async def place_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    return await CEXService.place_order(db, current_user.id, order_data)


from pydantic import BaseModel
class ExecuteRequest(BaseModel):
    order_id: int
    amount: float

@router.post("/execute/", response_model=dict)
async def execute_order(
    executeRequest: ExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    return await CEXService.execute_order(db, executeRequest.order_id, current_user, executeRequest.amount)

@router.get("/order_book/{symbol}", response_model=list[OrderResponse])
async def get_order_book(symbol: str, db: AsyncSession = Depends(get_db)):
    return await CEXService.get_order_book(db, symbol)


class OrderBookResponse(BaseModel):
    order: OrderResponse
    email: str
@router.get("/order_book/", response_model=list[OrderBookResponse])
async def get_order_book(db: AsyncSession = Depends(get_db)):
    return await CEXService.get_orders(db)