import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import get_db
from services.cex_service import CEXService

async def update_prices_task():
    while True:
        async for db in get_db():
            await CEXService.update_prices(db)
        await asyncio.sleep(1)
