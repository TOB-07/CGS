from asyncpg import Connection


async def insert_games(game_name: str, conn: Connection):
    await conn.execute("INSERT INTO games(game_name) VALUES ($1)", game_name)


async def insert_saves(modified_at: str, path: str, save_hash: str, game_id:int, user_id:int, conn: Connection):
    await conn.execute(
        "INSERT INTO saves(modified_at, path, save_hash, game_id, user_id) VALUES ($1,$2,$3,$4,$5)",
        modified_at,
        path,
        save_hash,
        game_id,
        user_id,
    )

