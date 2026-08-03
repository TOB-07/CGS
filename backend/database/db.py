import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()

pool = None

async def connect():
    global pool

    pool = await asyncpg.create_pool(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSW"),
        database="myapp",
        min_size=2,
        max_size=10,
    )

async def disconnect():
    await pool.close()

async def get_db():
    async with pool.acquire() as conn:
        yield conn
