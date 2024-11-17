import os
import httpx
from pydantic import BaseModel
from typing import List, Optional, Dict

class Status(BaseModel):
    timestamp: str
    error_code: int
    error_message: Optional[str]
    elapsed: int
    credit_count: int

class Quote(BaseModel):
    price: float
    volume_24h: float
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    market_cap: float
    market_cap_dominance: float
    fully_diluted_market_cap: float
    last_updated: str

class CryptoData(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str
    num_market_pairs: int
    date_added: str
    tags: List[str]
    max_supply: Optional[int]
    circulating_supply: float
    total_supply: float
    platform: Optional[str]
    cmc_rank: int
    last_updated: str
    quote: Dict[str, Quote]

class CoinMarketCapResponse(BaseModel):
    status: Status
    data: Dict[str, CryptoData]

from dotenv import load_dotenv
load_dotenv(".env")


url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=USDT&convert=USDT"
api_key = os.getenv("COIN_MARKET_API_KEY")
response = httpx.get(url, headers={"X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_API_KEY"), "Accept": "application/json"})

# pair: CoinMarketCapResponse = CoinMarketCapResponse(**response.json())
pair = response.json()
print(pair['data']['USDT']['quote']['USDT']['price'])

