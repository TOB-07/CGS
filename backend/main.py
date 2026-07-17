from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi import status
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
        username VARCHAR(20) UNIQUE NOT NULL,
        password VARCHAR(20) NOT NULL
        )
        """
    )

    yield

    await app.state.conn.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="frontend/static"))


async def find_user(username: str) -> bool:
    db_username = await app.state.conn.fetchval(
        "SELECT username FROM users WHERE username=$1", username
    )

    if username == db_username:
        return True
    else:
        return False


def check_password(password: str) -> str:
    if not (8 <= len(password) <= 16):
        return "Password must contain atleast 8-16 characters"
    if not any(char.islower() for char in password):
        return "Password must contain a small letter"
    if not any(char.isupper() for char in password):
        return "Password must contain a capital letter"
    if not any(char.isdigit() for char in password):
        return "Password must contain a digit"
    if not any(not char.isalnum() for char in password):
        return "Password must contain a special character"

    return "Correct"


@app.get("/")
async def webpage():
    return FileResponse("frontend/index.html")

@app.post("/user_reg")
async def reg(username: str = Form(...), password: str = Form(...)):
    if await find_user(username):
        return {"msg": "Username already exists"}

    result = check_password(password)

    if result != "Correct":
        return {"message": result}

    await app.state.conn.execute(
        """
            INSERT INTO users (username, password)
            VALUES ($1, $2)
            """,
        username,
        password,
    )

    return RedirectResponse(
        url= f"/?registered=true&username={username}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/check_user/{username}")
async def check_user(username: str):
    if await find_user(username):
        return {"availability": False}
    else:
        return {"availability": True}
    

@app.get("/dashboard")
async def dashborad():
    return FileResponse("frontend/dashboard.html")

@app.post("/user_log")
async def login(username: str =Form(...), password:str = Form(...) ):
    db_username = await app.state.conn.fetchval("SELECT username FROM users WHERE username=$1 AND password=$2",username,password)

    if (db_username == username):
        return RedirectResponse(
            url = f"/dashboard?username={username}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    else :
        return RedirectResponse(
            url="/?pwd=incorrect",
            status_code=status.HTTP_303_SEE_OTHER
        )
