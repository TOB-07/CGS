# Retrieving metadata from local

import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from backend.database import db
from backend.database import uploads as db_actions
from backend.database.sync import retrieve_manifest
from backend.services.uploads import delete_file, upload
from backend.utils.fileexplorer import FileExplorer

load_dotenv()

config_file_path = os.getenv("CONFIG_FILE")
seaweedfs = os.getenv("SEAWEEDFS")

if os.path.exists(config_file_path):
    with open(config_file_path, "r") as file:
        config = json.load(file)

local_MGS = Path(config["path"])
remote_MGS = "/upload/MGS"


def fetch_local_data() -> dict:

    fe = FileExplorer()
    fe.explore_folder(Path(config["path"]))

    local = {}

    for file_path, hash, m_time in zip(fe.file_paths, fe.save_hashes, fe.modified_at):
        # print(f"{file_name} - {hash}")
        rel = str(Path(file_path).relative_to(local_MGS))
        local[rel] = {"abs_path": file_path, "hash": hash, "modified_at": m_time}

    return local


# Retrieving metadata from remote


async def retrieve_remote_metadata(
    client: httpx.AsyncClient, path: str = "/upload/MGS"
):
    response = await client.get(
        f"{seaweedfs}{path}", headers={"Accept": "application/json"}
    )

    return response.json()


async def fetch_remote_data() -> dict:
    folder_paths = []
    file_paths = []
    file_hashes = []
    file_modified_at = []

    async with httpx.AsyncClient() as client:
        data = await retrieve_remote_metadata(client)

        for entry in data["Entries"]:
            if entry["FileSize"] == 0:
                folder_paths.append(entry["FullPath"])
            else:
                file_paths.append(entry["FullPath"])
                file_hashes.append(entry["Md5"])
                file_modified_at.append(entry["Mtime"])

        the_folder_paths = folder_paths.copy()

        while folder_paths:
            folder = folder_paths.pop()

            data = await retrieve_remote_metadata(client, folder)

            for entry in data["Entries"]:
                if entry["FileSize"] == 0:
                    folder_paths.append(entry["FullPath"])
                    the_folder_paths.append(entry["FullPath"])
                else:
                    file_paths.append(entry["FullPath"])
                    file_hashes.append(entry["Md5"])
                    file_modified_at.append(entry["Mtime"])

    remote = {}

    for file_path, hash, m_time in zip(file_paths, file_hashes, file_modified_at):
        rel = str(Path(file_path).relative_to(remote_MGS))
        remote[rel] = {
            "full_path": file_path,
            "hash": hash,
            "modified_at": m_time,
        }

    return remote


# Retrieving metadata from manifest


async def fetch_manifest_data() -> dict:
    rows = await retrieve_manifest()

    return {
        str(Path(row["path"]).relative_to(local_MGS)): row["save_hash"] for row in rows
    }


async def _local_fetch_manifest_data():
    await db.connect()

    try:
        data = await fetch_manifest_data()
    finally:
        await db.disconnect()

    return data


# Database actions
async def _upsert_manifest(
    rel_path: str, abs_path: str, file_hash: str, modified_at, user_id: int
):
    game_name = Path(rel_path).parts[0]
    game_id = await db_actions.get_game_id(game_name)
    if game_id is None:
        await db_actions.insert_games_created(game_name)
        game_id = await db_actions.get_game_id(game_name)

    save_id = await db_actions.get_save_id(abs_path)
    if save_id is None:
        await db_actions.insert_saves_created(game_id, user_id, modified_at,abs_path, file_hash)
    else:
        await db_actions.insert_saves_modified(save_id, modified_at, file_hash)


async def _remove_manifest(abs_path: str):
    save_id = await db_actions.get_save_id(abs_path)
    if save_id is not None:
        await db_actions.save_deleted(save_id)


# File actions
async def _upload_local_file(abs_path: str):
    fe = FileExplorer()
    fe.explore_file(Path(abs_path))
    await upload(fe)


async def _download_remote_file(remote_full_path: str, abs_local_path: str):
    Path(abs_local_path).parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{seaweedfs}{remote_full_path}")

        with open(abs_local_path, "wb") as f:
            f.write(response.content)  


async def _delete_local_file(abs_path: str):
    Path(abs_path).unlink(missing_ok=True)


async def the_sync(user_id: int = 1):
    local = fetch_local_data()
    remote = await fetch_remote_data()
    manifest = await fetch_manifest_data()

    all_paths = (
        set(local) | set(remote) | set(manifest)
    )  

    for rel_path in all_paths:
        l = local.get(rel_path)
        r = remote.get(rel_path)
        m = manifest.get(rel_path)
        abs_local_path = str(local_MGS / rel_path)  

        # Case 1: Present everywhere
        if l and r and m:
            if l["hash"] != r["hash"]:
                if l["modified_at"] > r["modified_at"]:
                    await _upload_local_file(l["abs_path"])
                    await _upsert_manifest(
                        rel_path, l["abs_path"], l["hash"], l["modified_at"], user_id
                    )
                else:
                    await _download_remote_file(r["full_path"], abs_local_path)
                    await _upsert_manifest(
                        rel_path, abs_local_path, r["hash"], r["modified_at"], user_id
                    )

        # Case 2: Local and manifest only
        elif l and m and not r:
            if l["hash"] == m:
                _delete_local_file(l["abs_path"])
                await _remove_manifest(l["abs_path"])
            else:
                await _upload_local_file(l["abs_path"])
                await _upsert_manifest(rel_path,l["abs_path"],l["hash"],l["modified_at"],user_id)

        # Case 3: Remote and manifest only
        elif r and m and not l:
            if r["hash"] == m:
                await delete_file(abs_local_path)
                await _remove_manifest(abs_local_path)
            else:
                await _download_remote_file(r["full_path"],abs_local_path)
                await _upsert_manifest(rel_path, abs_local_path, r["hash"], r["modified_at"], user_id)

        # Case 4: Local only
        elif l and not r and not m:
            await _upload_local_file(l["abs_path"])
            await _upsert_manifest(rel_path, l["abs_path"], l["hash"], l["modified_at"], user_id)

        # Case 5: remote only
        elif r and not l and not m:
            await _download_remote_file(r["full_path"], abs_local_path)
            await _upsert_manifest(rel_path, abs_local_path, r["hash"], r["modified_at"], user_id)

        # Case 6: manifest only
        elif m and not l and not r:
            await _remove_manifest(abs_local_path)

        # Case 7: Local and remote only, no manifest => Not synced 
        elif l and r and not m:
            if l["hash"] == r["hash"]:
                await _upsert_manifest(rel_path, l["abs_path"], l["hash"], l["modified_at"], user_id)
            else:
                print(f"Conflict no sync history: {rel_path} differs on local and remote")
                if l["modified_at"] > r["modifed_at"]:
                    await _upload_local_file(l["abs_path"])
                    await _upsert_manifest(rel_path, l["abs_path"], l["hash"], l["modified_at"], user_id)
                else:
                    await _download_remote_file(r["full_path"], abs_local_path)
                    await _upsert_manifest(rel_path, abs_local_path, r["hash"], r["modified_at"], user_id)


async def main():
    verbose = True

    local = fetch_local_data()
    remote = await fetch_remote_data()
    manifest = await _local_fetch_manifest_data()

    if verbose:
        print("Local")
        for key, value in local.items():
            print(f"{key} - {value}")
        print("------------------------------------------\n\n")

        print("Remote")
        for key, value in remote.items():
            print(f"{key} - {value}")
        print("------------------------------------------\n\n")

        print("Manifest")
        for key, value in manifest.items():
            print(f"{key} - {value}")
        print("------------------------------------------\n\n")


if __name__ == "__main__":
    asyncio.run(main())
