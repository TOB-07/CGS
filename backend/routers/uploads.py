import httpx
from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.post("/user_upload")
async def upload(upload: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8888/upload/{upload.filename}",
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