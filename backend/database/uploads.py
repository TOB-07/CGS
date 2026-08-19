from backend.database import db


async def insert_games_created(game_name: str):
    async with db.pool.acquire() as conn:

        await conn.execute("INSERT INTO games(game_name) VALUES ($1)", game_name)

async def insert_games_modified(game_name: str,game_id:int):
    async with db.pool.acquire() as conn:

        await conn.execute("UPDATE games SET game_name=$1 WHERE game_id=$2",game_name,game_id)


async def game_deleted(game_id: int):
    async with db.pool.acquire() as conn:

        await conn.execute("DELETE FROM games WHERE game_id=$1",game_id)


async def insert_saves_created(game_id:int, user_id:int,modified_at: str, path: str, save_hash: str):
    async with db.pool.acquire() as conn:

        await conn.execute(
            "INSERT INTO saves(game_id, user_id, modified_at, path, save_hash) VALUES ($1,$2,$3,$4,$5)",
            game_id,
            user_id,
            modified_at,
            path,
            save_hash,

        )

async def insert_saves_modified(save_id:int, modified_at: str, save_hash: str):
    async with db.pool.acquire() as conn:

        await conn.execute(
            "UPDATE saves SET modified_at=$1, save_hash=$2 WHERE save_id=$3",modified_at,save_hash,save_id
        )

async def insert_saves_moved(save_id:int, modified_at: str, path:str, save_hash:str):
    async with db.pool.acquire() as conn:

        await conn.execute(
            "UPDATE saves SET modified_at=$1, path=$2, save_hash=$3 WHERE save_id=$4",modified_at,path,save_hash,save_id
        )

async def save_deleted(save_id:int):
    async with db.pool.acquire() as conn:

        await conn.execute("DELETE FROM saves WHERE save_id=$1", save_id)


async def get_game_id(game_name:str):
    async with db.pool.acquire() as conn:

        return await conn.fetchval("SELECT game_id FROM games WHERE game_name=$1",game_name)

async def get_save_id(path:str):
    async with db.pool.acquire() as conn:

        return await conn.fetchval("SELECT save_id FROM saves WHERE path=$1",path)