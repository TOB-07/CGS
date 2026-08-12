from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.database.db import connect, disconnect, get_db
from backend.routers import uploads, users, webpage


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()

    async for conn in get_db():
        await conn.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(20) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL);
         
        CREATE TABLE IF NOT EXISTS games(
        game_id SERIAL PRIMARY KEY,
        game_name VARCHAR(30) UNIQUE NOT NULL);
         
        CREATE TABLE IF NOT EXISTS saves(
        save_id SERIAL PRIMARY KEY,
        game_id INTEGER NOT NULL REFERENCES games(game_id),
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        modified_at TIMESTAMPTZ NOT NULL,
        path VARCHAR(255) NOT NULL,
        save_hash VARCHAR(255) NOT NULL,
        version INTEGER NOT NULL DEFAULT 1);
         
        CREATE TABLE IF NOT EXISTS devices(
        device_id SERIAL PRIMARY KEY,
        device_uuid VARCHAR(255) UNIQUE NOT NULL,
        device_name VARCHAR(30) NOT NULL,
        platform VARCHAR(30) NOT NULL,
        user_id INTEGER NOT NULL REFERENCES users(user_id)); """)

    yield

    await disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(webpage.router)
app.include_router(uploads.router)

