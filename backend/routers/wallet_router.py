from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.wallet_service import WalletService
from ..database.connect import get_db
from ..schemas.wallet import WalletResponse, TransferRequest, WithdrawRequest, BalanceResponse
from ..models.user import User
from ..services.user_service import AuthService
router = APIRouter()



@router.post("/create", response_model=dict)
async def create_wallet(db: AsyncSession = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    wallet = await WalletService.create_wallet(db, current_user.id)
    return {"message": "success"}


from pydantic import BaseModel
class DepositRequest(BaseModel):
    crypto_symbol: str
    amount: float

@router.post("/deposit", response_model=BalanceResponse)
async def deposit_funds(
        deposit: DepositRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(AuthService.get_current_user)
):
    """
    Simulate depositing funds into the hot wallet for a specific cryptocurrency.
    """
    wallet = await WalletService.add_funds_to_wallet(db, current_user.id, deposit.crypto_symbol, deposit.amount)
    return wallet

@router.get('/balance', response_model=list[BalanceResponse])
async def get_balance(db: AsyncSession = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    wallet = await WalletService.get_wallet_balance(db, current_user)
    return wallet



@router.post("/transfer", response_model=dict)
async def transfer_from_cold_to_hot(request: TransferRequest, db: AsyncSession = Depends(get_db)):
    """
    Transfer funds from cold wallet to hot wallet.
    """
    return await WalletService.transfer_from_cold_to_hot(db, request.crypto_symbol, request.amount)

@router.post("/withdraw", response_model=WalletResponse)
async def withdraw_funds(request: WithdrawRequest, db: AsyncSession = Depends(get_db)):
    """
    Simulate withdrawing funds from the hot wallet for a specific cryptocurrency.
    """
    wallet = await WalletService.withdraw_from_hot_wallet(db, request.crypto_symbol, request.amount)
    return wallet
