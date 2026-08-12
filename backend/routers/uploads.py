import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import RedirectResponse

from backend.services.uploads import Worker

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

@router.post("/system_upload")
async def upload():
    Worker().the_work()
    return RedirectResponse(
        url="/dashboard?status=startedsync",
        status_code=status.HTTP_303_SEE_OTHER,
    )


