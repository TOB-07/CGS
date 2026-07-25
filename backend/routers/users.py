from argon2 import PasswordHasher
from asyncpg import Connection
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse

from backend.database.db import get_db
from backend.database.users import find_user, get_password, insert_user
from backend.services.passwords import check_password

router = APIRouter()
ph = PasswordHasher()

@router.post("/user_reg")
async def reg(username:str = Form(...), password: str = Form(...), conn: Connection  = Depends(get_db)):
    if await find_user(username, conn):
        return {"msg": "username already exists!"}

    result = check_password(password)

    if result != "Correct":
        return result

    user_password = ph.hash(password)

    await insert_user(username, user_password,conn)

    return RedirectResponse(
        url = f"/?registered=true&username={username}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/user_log")
async def login(username:str = Form(...), password:str = Form(...), conn: Connection = Depends(get_db)):
    db_user_password = await get_password(username, conn)

    if ph.verify(db_user_password, password):
        return RedirectResponse(
            url = f"/dashboard?username={username}",
            status_code = status.HTTP_303_SEE_OTHER
        )
    else:
        return RedirectResponse(
            url = "/?pwd=incorrect",
            status_code = status.HTTP_303_SEE_OTHER
        )

@router.get("/check_user/{username}")
async def check_user(username:str, conn: Connection = Depends(get_db)):
    if await find_user(username, conn):
        return {"availability": False}
    else:
        return {"availability": True}

    

    