from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.order import Order
from schemas.cex import OrderCreate
from datetime import datetime

class OrderRepository:
    @staticmethod
    async def create_order(db: AsyncSession, user_id: int, order_data: OrderCreate, price: float) -> Order:
        order = Order(
            user_id=user_id,
            type=order_data.type,
            trading_pair=order_data.trading_pair,
            price=price,
            amount=order_data.amount,
            created_at=datetime.now()
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | dict:
        result = await db.execute(select(Order).filter(Order.id == order_id))
        return result.scalars().first()

    @staticmethod
    async def get_order_book(db: AsyncSession, trading_pair: str):
        query = select(Order).filter(Order.trading_pair == trading_pair).order_by(Order.created_at)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_orders(db: AsyncSession):
        # query = select(Order).order_by(Order.created_at)
        # result = await db.execute(query)
        # return result.scalars().all()
        query = (
            select(Order, User.email)
            .join(User, Order.user_id == User.id)
            .order_by(Order.created_at)
        )
        result = await db.execute(query)
        # Combine Order data and User email into a list of dictionaries
        return [{"order": order, "email": email} for order, email in result.all()]

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int):
        query = await db.execute(select(Order).filter(Order.id == order_id))
        order = query.scalars().first()
        await db.execute(delete(Order).where(Order.id == order_id))
        await db.commit()
        return order
