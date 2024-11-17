from sqlalchemy import Column, Integer, String, Float, ForeignKey
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from ..database.connect import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    wallets = relationship("Wallet", back_populates="user")
