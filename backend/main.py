from fastapi import FastAPI
from routers import user_router, cex_router, wallet_router
from database.connect import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from tasks import update_prices_task


app = FastAPI()

origins = [
    "http://localhost:5173",  # Vite development server

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup():
    asyncio.create_task(update_prices_task())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Include routers
app.include_router(user_router.router, prefix="/auth")
app.include_router(cex_router.router, prefix="/order")
app.include_router(wallet_router.router, prefix="/wallet")


