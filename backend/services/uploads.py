import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from backend.utils.fileexplorer import FileExplorer

load_dotenv()

CONFIG_PATH = os.getenv("CONFIG_FILE")
SEAWEEDFS = os.getenv("SEAWEEDFS")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH,"r") as f:
        config_file = json.load(f)

async def auto_upload():
    fe = FileExplorer()
    fe.find_path(Path(config_file["path"]))

    async with httpx.AsyncClient() as client:
        for file_path, name, data, content_type in zip(
            fe.file_paths,
            fe.file_names,
            fe.file_data,
            fe.file_type
        ):
            response = await client.post(
                f"{SEAWEEDFS}/upload/{file_path}",
                files={
                    "file": (
                        name,
                        data,
                        content_type,
                    )
                },
            )

            if not response.is_success:
                print(f"{name} failed : {response.status_code}")

async def main():
    await auto_upload()

if __name__ == "__main__":
    asyncio.run(main())