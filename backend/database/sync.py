from typing import cast

from asyncpg import Connection

from backend.database import db


async def retrieve_manifest():
    async with db.pool.acquire() as conn:
        # conn = cast(Connection,conn)
        rows = await conn.fetch("SELECT path, save_hash FROM saves WHERE user_id=1")


    return rows
        