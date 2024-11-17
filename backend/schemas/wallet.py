from pydantic import BaseModel

class WalletResponse(BaseModel):
    crypto_symbol: str
    wallet_type: str
    balance: float

    class Config:
        orm_mode = True

class TransferRequest(BaseModel):
    crypto_symbol: str
    amount: float

class WithdrawRequest(BaseModel):
    crypto_symbol: str
    amount: float


class BalanceResponse(BaseModel):
    id: int
    wallet_id: int
    crypto_symbol: str
    balance: float