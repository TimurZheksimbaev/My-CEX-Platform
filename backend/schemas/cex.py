from pydantic import BaseModel
from datetime import datetime
class OrderCreate(BaseModel):
    type: str
    trading_pair: str
    amount: float

class OrderResponse(BaseModel):
    id: int
    type: str
    trading_pair: str
    price: float
    amount: float
    created_at: datetime

class PriceResponse(BaseModel):
    symbol: str
    price: float
