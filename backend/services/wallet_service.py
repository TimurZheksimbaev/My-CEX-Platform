from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.wallet import Wallet, WalletType, Balance
from fastapi import HTTPException, status, Depends
from models.user import User

class WalletService:

    @staticmethod
    async def create_wallet(db: AsyncSession, user_id: int):
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        return wallet

    @staticmethod
    async def get_wallet(db: AsyncSession, wallet_id: int) -> Wallet:
        query = await db.execute(select(Wallet).filter(Wallet.id == wallet_id))
        wallet = query.scalars().first()
        # if not wallet:
        #     # Create wallet if it does not exist
        #     wallet = Wallet(user_id=user.id, balance=0.0)
        #     db.add(wallet)
        #     await db.commit()
        #     await db.refresh(wallet)
        return wallet

    @staticmethod
    async def get_wallet_by_user_id(db: AsyncSession, user_id: int) -> Wallet:
        result = await db.execute(select(Wallet).filter(Wallet.user_id == user_id))
        return result.scalars().first()

    # @staticmethod
    # async def add_funds_to_wallet(db: AsyncSession, user: User, crypto_symbol: str, amount: float):
    #     hot_wallet = await WalletService.get_wallet_by_user_id(db, user.id)
    #     if hot_wallet.crypto_symbol == crypto_symbol:
    #         hot_wallet.balance += amount
    #     else:
    #         hot_wallet.crypto_symbol = crypto_symbol
    #         hot_wallet.balance = amount
    #     await db.commit()
    #     return hot_wallet

    @staticmethod
    async def add_funds_to_wallet(db: AsyncSession, user_id: int, crypto_symbol: str, amount: float):
        wallet = await WalletService.get_wallet_by_user_id(db, user_id)
        result = await db.execute(
            select(Balance).where(Balance.wallet_id == wallet.id).where(Balance.crypto_symbol == crypto_symbol)
        )
        balance = result.scalars().first()

        if balance:
            balance.balance += amount
        else:
            balance = Balance(wallet_id=wallet.id, crypto_symbol=crypto_symbol, balance=amount)
            db.add(balance)

        await db.commit()
        await db.refresh(balance)
        return balance
    
    @staticmethod
    async def get_wallet_balance(db: AsyncSession, user: User):
        wallet = await WalletService.get_wallet_by_user_id(db, user.id)
        result = await db.execute(
            select(Balance).where(Balance.wallet_id == wallet.id)
        )
        balances = result.scalars().all()

        if balances:
            return balances
        else:
            return {"message": "You do not have crypto"}

    # @staticmethod
    # async def pay_crypto(db: AsyncSession, wallet_id: int, cost: float, crypto_symbol: str):
    #     wallet = await WalletService.get_wallet(db, wallet_id)
    #     if wallet.balance < cost:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    #     if wallet.crypto_symbol == crypto_symbol:
    #         wallet.balance -= cost
    #     await db.commit()
    #     await db.refresh(wallet)
    #     return wallet
    #
    # @staticmethod
    # async def get_crypto(db: AsyncSession, wallet_id: int, cost: float, crypto_symbol: str):
    #     wallet = await WalletService.get_wallet(db, wallet_id)
    #     if wallet.crypto_symbol == crypto_symbol:
    #         wallet.balance += cost
    #     else:
    #         wallet.crypto_symbol = crypto_symbol
    #         wallet.balance = cost
    #     await db.commit()
    #     await db.refresh(wallet)
    #     return wallet

    # @staticmethod
    # async def pay_crypto(db: AsyncSession, wallet_id: int, price: float, amount: float, crypto_symbol: str):
    #     crypto_from, crypto_to = crypto_symbol.split("-")
    #     wallet = await WalletService.get_wallet(db, wallet_id)
    #     query = await db.execute(select(Balance).filter(Balance.wallet_id == wallet.id))
    #     balances = query.scalars().all()
    #     found = False
    #     for balance in balances:
    #         if balance.crypto_symbol == crypto_from:
    #             # if crypto already exists then just increase
    #             balance.balance += amount
    #             await db.commit()
    #             found = True
    #
    #         # checking if crypto_to exists
    #         if balance.crypto_symbol == crypto_to:
    #             balance.balance -= price*amount
    #             await db.commit()
    #             await db.refresh(balance)
    #     if not found:
    #         balance_to = Balance(wallet_id=wallet.id, crypto_symbol=crypto_from, balance=amount)
    #         db.add(balance_to)
    #         await db.commit()
    #
    #
    #
    # @staticmethod
    # async def get_crypto(db: AsyncSession, wallet_id: int, price: float, amount: float, crypto_symbol: str):
    #     crypto_from, crypto_to = crypto_symbol.split("-")
    #     wallet = await WalletService.get_wallet(db, wallet_id)
    #     query = await db.execute(select(Balance).filter(Balance.wallet_id == wallet.id))
    #     balances = query.scalars().all()
    #     for balance in balances:
    #         if balance.crypto_symbol == crypto_to:
    #             balance.balance += price*amount
    #             await db.commit()
    #             await db.refresh(balance)
    #             return balance

    @staticmethod
    async def exchange_crypto(
            db: AsyncSession,
            wallet_from_id: int,
            wallet_to_id: int,
            amount_from: float,
            amount_to: float,
            trading_pair: str,
    ):
        crypto_from, crypto_to = trading_pair.split("-")

        # Fetch balances for both wallets
        wallet_from_balances = await db.execute(
            select(Balance).filter(Balance.wallet_id == wallet_from_id)
        )
        wallet_to_balances = await db.execute(
            select(Balance).filter(Balance.wallet_id == wallet_to_id)
        )

        balances_from = {b.crypto_symbol: b for b in wallet_from_balances.scalars().all()}
        balances_to = {b.crypto_symbol: b for b in wallet_to_balances.scalars().all()}

        # Subtract from `crypto_from` balance
        if crypto_from not in balances_from or balances_from[crypto_from].balance < amount_from:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance for trade")
        balances_from[crypto_from].balance -= amount_from

        # Add to `crypto_from` balance in the receiving wallet
        if crypto_from in balances_to:
            balances_to[crypto_from].balance += amount_from
        else:
            db.add(Balance(wallet_id=wallet_to_id, crypto_symbol=crypto_from, balance=amount_from))

        # Subtract from `crypto_to` balance in the receiving wallet
        if crypto_to in balances_to:
            balances_to[crypto_to].balance -= amount_to
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receiving wallet insufficient funds")

        # Add to `crypto_to` balance in the sending wallet
        if crypto_to in balances_from:
            balances_from[crypto_to].balance += amount_to
        else:
            db.add(Balance(wallet_id=wallet_from_id, crypto_symbol=crypto_to, balance=amount_to))

        await db.commit()


    @staticmethod
    async def trade_crypto(
        db: AsyncSession, buyer_id: int, seller_id: int, trading_pair: str, amount: float, price: float
    ):    
        """
        Executes a trade between buyer and seller.

        Args:
            db: Database session.
            buyer_id: ID of the buyer.
            seller_id: ID of the seller.
            trading_pair: Crypto trading pair (e.g., BTC-USDT).
            amount: Amount of the base crypto being traded.
            price: Current price of the trading pair.

        Returns:
            A dictionary containing the status of the trade.
        """
        # Calculate total cost
        total_cost = amount * price
        base_crypto, quote_crypto = trading_pair.split("-")

        # Get wallets
        buyer_wallet = await WalletService.get_wallet_by_user_id(db, buyer_id)
        seller_wallet = await WalletService.get_wallet_by_user_id(db, seller_id)

        # Check balances
        buyer_balance = await db.execute(
            select(Balance).filter(Balance.wallet_id == buyer_wallet.id, Balance.crypto_symbol == quote_crypto)
        )
        buyer_balance = buyer_balance.scalars().first()

        seller_balance = await db.execute(
            select(Balance).filter(Balance.wallet_id == seller_wallet.id, Balance.crypto_symbol == base_crypto)
        )
        seller_balance = seller_balance.scalars().first()

        if not buyer_balance or buyer_balance.balance < total_cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient buyer balance")

        if not seller_balance or seller_balance.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient seller balance")

        # Perform trade
        buyer_balance.balance -= total_cost
        seller_balance.balance -= amount    

        await WalletService.add_funds_to_wallet(db, buyer_wallet, base_crypto, amount)
        await WalletService.add_funds_to_wallet(db, seller_wallet, quote_crypto, total_cost)

        await db.commit()

        return {"message": "Trade executed successfully", "amount": amount, "price": price}


