from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from enum import Enum as PyEnum
from ..database.connect import Base
from sqlalchemy.orm import relationship


class WalletType(PyEnum):
    HOT = "hot"
    COLD = "cold"


# class Wallet(Base):
#     __tablename__ = "wallets"
#
#     id = Column(Integer, primary_key=True, index=True)
#     crypto_symbol = Column(String, default="USDT")  # e.g., BTC, ETH
#     wallet_type = Column(String, default='hot')  # HOT or COLD
#     balance = Column(Float, default=0.0)  # The balance held in this wallet
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     user = relationship("User", back_populates="wallets")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="wallets")
    balances = relationship("Balance", back_populates="wallet")

class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    crypto_symbol = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    wallet = relationship("Wallet", back_populates="balances")