from asyncpg import Connection


async def find_user(username:str, conn: Connection) -> bool:
    
    db_username = await conn.fetchval("SELECT username FROM users WHERE username=$1",username)

    return db_username == username

async def insert_user(username:str, password:str, conn: Connection) :
    
    await conn.execute("""
    INSERT INTO users(username, password_hash)
    VALUES ($1, $2)
    
    """,
    username,
    password,)


async def get_password(username:str, conn: Connection) -> str:

    return await conn.fetchval("SELECT password_hash FROM users WHERE username=$1",username)

    

