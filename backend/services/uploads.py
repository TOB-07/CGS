import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from backend.utils.fileexplorer import FileExplorer

load_dotenv()

config_file_path = os.getenv("CONFIG_FILE")
SEAWEEDFS = os.getenv("SEAWEEDFS")

if os.path.exists(config_file_path):
    with open(config_file_path,"r") as file:
        config = json.load(file)


fe = FileExplorer()

async def upload(fe: FileExplorer):
    success = True
    async with httpx.AsyncClient() as client:
        for file_path, name, data, content_type in zip(
            fe.file_paths, fe.file_names, fe.file_data, fe.file_type,
        ):
            response = await client.post(
                f"{SEAWEEDFS}/upload/{file_path}",
                files={
                    "file": (name, data, content_type)
                },
            )

            if not response.is_success:
                print(f"{name} failed to upload: {response.status_code}")
                success = False

    return success

async def delete_file(file_path : str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{SEAWEEDFS}/upload/{file_path}")

        if not response.is_success:
            print(f"Failed to delete {file_path}: {response.status_code}")

async def delete_folder(folder_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{SEAWEEDFS}/upload/{folder_path}",params={"recursive": "true"})

        if not response.is_success:
            print(f"Failed to delete folder {folder_path} : {response.status_code}" )

class TheEventHandler(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent, verbose = False):
        if not event.is_directory:
            fe.explore_file(Path(event.src_path))
            asyncio.run(upload(fe))
            if verbose:
                print(f"File Created: {event.src_path}")
                print("------------------------------------------")
        else:
            if verbose:
                fe.explore_folder(Path(event.src_path))
                print(f"Folder created: {event.src_path}")
                print(f"Folder names: {fe.folder_names}")
                print(f"Folder paths: {fe.folder_paths}")
                print("------------------------------------------")            

        fe.clear()

    def on_modified(self, event: FileSystemEvent, verbose = False):
        if not event.is_directory:
            fe.explore_file(Path(event.src_path))
            asyncio.run(upload(fe))
            if verbose:
                print(f"File Created: {event.src_path}")
                print("------------------------------------------")
            else:
                if verbose:
                    fe.explore_folder(Path(event.src_path))
                    print(f"Folder created: {event.src_path}")
                    print(f"Folder names: {fe.folder_names}")
                    print(f"Folder paths: {fe.folder_paths}")
                    print("------------------------------------------")            

        fe.clear()

    def on_moved(self, event: FileSystemEvent, verbose = False):
        if not event.is_directory:
            fe.explore_file(Path(event.dest_path))
            upload_status = asyncio.run(upload(fe))

            if upload_status:
                asyncio.run(delete_file(event.src_path))

            if verbose:
                print(f"file moved: {event.src_path} -> {event.dest_path}")

        else:
            fe.explore_folder(Path(event.dest_path))
            upload_status = asyncio.run(upload(fe))

            if upload_status:
                asyncio.run(delete_folder(event.src_path))

            if verbose:
                print(f"Folder moved: {event.src_path} -> {event.dest_path}")
                print(f"Folder names: {fe.folder_names}")
                print(f"Folder paths: {fe.folder_paths}")
                print("------------------------------------------")

        fe.clear()



    def on_deleted(self, event: FileSystemEvent, verbose = False):
        if not event.is_directory:
            asyncio.run(delete_file(event.src_path))
            if verbose:
                print(f"Deleted file: {event.src_path}")
                print("------------------------------------------")
        else:
            asyncio.run(delete_folder(event.src_path))
            if verbose:
                print(f"Deleted folder: {event.src_path}")
                print("------------------------------------------")
        

class Worker:
    def __init__(self):
        self.observer = Observer()
        self.event_handler = TheEventHandler()
        self.path = config["path"]


    def the_start(self):
        self.observer.schedule(self.event_handler,self.path,recursive=True)
        self.observer.start()

    def the_stop(self):
        self.observer.stop()
        self.observer.join()

    # def the_work(self):
        
    #     self.observer.schedule(self.event_handler,self.path,recursive=True)
    #     self.observer.start()

    #     try:
    #         while self.observer.is_alive():
    #             self.observer.join(10)
    #     finally:
    #         self.observer.stop()
    #         self.observer.join()

def main():
    Worker().the_work()

if __name__ == "__main__":
    main()