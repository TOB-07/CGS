import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from backend.database import db
from backend.database.uploads import insert_games, insert_saves
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
        for file_path, file_name, file_data, content_type, folder_name, save_hash, modified_at in zip(
            fe.file_paths,
            fe.file_names,
            fe.file_data,
            fe.file_type,
            fe.folder_names,
            fe.save_hashes,
            fe.modified_at,
        ):
            response = await client.post(
                f"{SEAWEEDFS}/upload/{file_path}",
                files={
                    "file": (
                        file_name,
                        file_data,
                        content_type,
                    )
                },
            )

            if response.is_success:
                async with db.pool.acquire() as conn:
                    await insert_games(folder_name, conn)
                    game_id = await conn.fetchval("SELECT game_id FROM games WHERE game_name=$1",folder_name)
                    username = "john"
                    user_id = await conn.fetchval("SELECT user_id FROM users WHERE username=$1",username)
                    await insert_saves(modified_at, file_path, save_hash, game_id, user_id, conn)
            else:
                print(f"{file_name} failed to upload : {response.status_code}")
        

async def main():
    await auto_upload()

if __name__ == "__main__":
    asyncio.run(main())