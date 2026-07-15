from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import asyncpg

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.conn = await asyncpg.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSW"),
        database="myapp",
    )

    await app.state.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username VARCHAR(20) NOT NULL,
        password VARCHAR(20) NOT NULL
        )
        """
    )

    yield

    await app.state.conn.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="frontend/static"))


@app.get("/")
async def webpage():
    return FileResponse("frontend/index.html")


@app.post("/user_reg")
async def reg(username: str = Form(...), password: str = Form(...)):
    await app.state.conn.execute(
        """
            INSERT INTO users (username, password)
            VALUES ($1, $2)
            """,
        username,
        password,
    )

    return {"message": "User Registered!"}

@app.get("/check_user/{username}")
async def check_user(username: str):
    db_username = await app.state.conn.fetchval("SELECT username FROM users WHERE username=$1", username)

    if db_username != username :
        return {"availability" : True}
    else :
        return {"availability" : False}

