import os

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repostories.order_repository import OrderRepository
from schemas.cex import OrderCreate, PriceResponse
from services.wallet_service import WalletService
from sqlalchemy import select, update
from datetime import datetime
from models.order import Order
from models.user import User
from dotenv import load_dotenv
load_dotenv(".env")

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"

class CEXService:

    @staticmethod
    async def update_prices(db: AsyncSession):
        # Fetch all distinct trading pairs from orders
        query = select(Order.trading_pair).distinct()
        result = await db.execute(query)
        trading_pairs = result.scalars().all()

        for trading_pair in trading_pairs:
            # Fetch the latest price for the trading pair
            price_response = await CEXService.fetch_crypto_price(trading_pair)
            price = price_response.price

            # Update all orders with the new price
            await db.execute(
                update(Order)
                .where(Order.trading_pair == trading_pair)
                .values(price=price)
            )

        await db.commit()

    @staticmethod
    async def fetch_crypto_price(symbol: str) -> PriceResponse:
        symbol = symbol.split("-")
        symbol = "".join(symbol)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BINANCE_API_URL}?symbol={symbol}")
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
            data = response.json()
            return PriceResponse(symbol=symbol, price=float(data["price"]))

    # @staticmethod
    # async def fetch_crypto_price(symbol: str) -> PriceResponse:
    #     symbol = symbol.split("-")
    #     url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    #     api_key = os.getenv("COIN_MARKET_API_KEY")
    #     parameters = {
    #         'symbol': symbol[0],
    #         'convert': symbol[1]
    #     }
    #     headers = {
    #         'Accept': 'application/json',
    #         'X-CMC_PRO_API_KEY': api_key,
    #     }
    #     async with httpx.AsyncClient() as client:

    #         response = await client.get(url, headers=headers, params=parameters)
    #         if response.status_code != 200:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
    #         data = response.json()
    #         return PriceResponse(symbol="".join(symbol), price=float(data['data'][symbol[0]]['quote'][symbol[1]]['price']))

    # @staticmethod
    # async def execute_order(db: AsyncSession, order_id: int, user: User, amount: float):
    #     # get order by id
    #     order: Order = await OrderRepository.get_order_by_id(db, order_id)
    #     if not order:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    #     if order.user_id == user.id:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot execute your own order")
    #
    #     # calculate total cost
    #     total_cost = order.price * order.amount
    #     if amount < order.amount:
    #         cost = order.price * amount
    #         total_cost -= cost
    #     else:
    #         cost = order.price * order.amount
    #         total_cost -= cost
    #
    #     # get wallets
    #     order_owner_wallet = await WalletService.get_wallet_by_user_id(db, order.user_id)
    #     current_user_wallet = await WalletService.get_wallet_by_user_id(db, user.id)
    #     if order.type == 'buy':
    #         await WalletService.pay_crypto(db, order_owner_wallet.id, cost, order.trading_pair)
    #         await WalletService.get_crypto(db, current_user_wallet.id, cost, order.trading_pair)
    #     elif order.type == 'sell':
    #         await WalletService.pay_crypto(db, current_user_wallet.id, cost, order.trading_pair)
    #         await WalletService.get_crypto(db, order_owner_wallet.id, cost, order.trading_pair)
    #     else:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order type")
    #
    #     # if crypto is ended then delete order
    #     if amount < order.amount:
    #         order.amount -= amount
    #         await db.commit()
    #     else:
    #         await OrderRepository.delete_order(db, order_id)
    #
    #     if total_cost == 0:
    #         await OrderRepository.delete_order(db, order_id)
    #     return {'message': "Order has been successfully executed!"}

    # @staticmethod
    # async def execute_order(db: AsyncSession, order_id: int, user: User, amount: float):
    #     # get order by id
    #     order: Order = await OrderRepository.get_order_by_id(db, order_id)
    #     if not order:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    #     if order.user_id == user.id:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot execute your own order")
    #
    #     # calculate total cost
    #     total_cost = order.price * order.amount
    #     if amount < order.amount:
    #         cost = order.price * amount
    #         total_cost -= cost
    #     else:
    #         cost = order.price * order.amount
    #         total_cost -= cost
    #
    #     # get wallets
    #     order_owner_wallet = await WalletService.get_wallet_by_user_id(db, order.user_id)
    #     current_user_wallet = await WalletService.get_wallet_by_user_id(db, user.id)
    #     if order.type == 'buy':
    #         await WalletService.pay_crypto(db, order_owner_wallet.id, order.price, amount, order.trading_pair)
    #         await WalletService.get_crypto(db, current_user_wallet.id, order.price, amount, order.trading_pair)
    #     elif order.type == 'sell':
    #         await WalletService.pay_crypto(db, current_user_wallet.id, order.price, amount, order.trading_pair)
    #         await WalletService.get_crypto(db, order_owner_wallet.id, order.price, amount, order.trading_pair)
    #     else:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order type")
    #
    #     # if crypto is ended then delete order
    #     if amount < order.amount:
    #         order.amount -= amount
    #         await db.commit()
    #     else:
    #         await OrderRepository.delete_order(db, order_id)
    #
    #     if total_cost == 0:
    #         await OrderRepository.delete_order(db, order_id)
    #     return {'message': "Order has been successfully executed!"}

    @staticmethod
    async def execute_order(db: AsyncSession, order_id: int, user: User, amount: float):

        # Fetch the order by ID
        order: Order = await OrderRepository.get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.user_id == user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot execute your own order")

        # Validate the amount
        if amount > order.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Amount {amount} exceeds available order quantity {order.amount}"
            )

        # Perform the trade using trade_crypto
        try:
            buyer_id = 0
            seller_id = 0
            if order.type == 'buy':
                buyer_id = order.user_id
                seller_id = user.id
            if order.type == 'sell':
                buyer_id = user.id
                seller_id = order.user_id

            trade_result = await WalletService.trade_crypto(
                db=db,
                buyer_id=buyer_id,
                seller_id=seller_id,
                trading_pair=order.trading_pair,
                amount=amount,
                price=order.price
            )
        except HTTPException as e:
            # Propagate the exception if something goes wrong during the trade
            raise e

        # Update or delete the order based on remaining amount
        try:
            async with db.begin():
                if amount < order.amount:
                    order.amount -= amount
                    await db.commit()
                else:
                    await OrderRepository.delete_order(db, order_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update or delete the order"
            )

        # Return the result from the trade_crypto function with additional details
        return {
            "message": "Order executed successfully!",
            **trade_result,
            "order_id": order_id,
            "remaining_order_amount": order.amount if amount < order.amount else 0,
        }


    @staticmethod
    async def place_order(db: AsyncSession, user_id: int, order_data: OrderCreate):
        """
        Place an order. For market orders, fetch the price from Binance.
        """
        # Fetch price for market order
        price_response = await CEXService.fetch_crypto_price(order_data.trading_pair)
        price = price_response.price

        total_cost = price * order_data.amount

        # Create the order
        order = await OrderRepository.create_order(
            db, user_id=user_id, order_data=order_data, price=price
        )
        return order

    @staticmethod
    async def get_order_book(db: AsyncSession, trading_pair: str):
        return await OrderRepository.get_order_book(db, trading_pair)

    @staticmethod 
    async def get_orders(db: AsyncSession):
        return await OrderRepository.get_orders(db)