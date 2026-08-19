import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, File, Request, UploadFile, status
from fastapi.responses import RedirectResponse

from backend.services.uploads import Worker

worker = None

load_dotenv()

SEAWEEDFS = os.getenv("SEAWEEDFS")

router = APIRouter()

@router.post("/user_file_upload")
async def upload_file(upload: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SEAWEEDFS}/upload/{upload.filename}",
            files={
                "file": (
                    upload.filename,
                    upload.file,
                    upload.content_type,
                )
            },
        )

        if response.is_success:
            return RedirectResponse(
                url="/dashboard?status=success",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            return RedirectResponse(
                url="/dashboard?status=failure",
                status_code = status.HTTP_303_SEE_OTHER,
            )

@router.post("/system_upload_start")
async def upload_start(request: Request):
    global worker
    if worker is None or not worker.observer.is_alive():
        worker = Worker(loop=request.app.state.loop)
        worker.the_start()
    
    return RedirectResponse(
        url="/dashboard?status=startedsync",
        status_code=status.HTTP_303_SEE_OTHER,
    )

@router.post("/system_upload_stop")
async def upload_stop():
    global worker
    if worker is not None and worker.observer.is_alive():
        worker.the_stop()

    return RedirectResponse(
        url="/dashboard?status=stoppedsync",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    

