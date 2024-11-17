from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from datetime import datetime
from ..database.connect import Base
import enum

class OrderType(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, index=True)  # "buy" or "sell"
    trading_pair = Column(String, index=True)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
