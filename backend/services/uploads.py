import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

import backend.database.uploads as db_actions
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
    def __init__(self, loop):
        self.loop = loop

    def on_created(self, event: FileSystemEvent, verbose = True):
        if not event.is_directory:
            fe.explore_file(Path(event.src_path))
            asyncio.run(upload(fe))
            if verbose:
                print(f"From FE: fe called and uploaded {event.src_path} to seaweedfs")
                print(f"File Created: {event.src_path}")
                print("------------------------------------------")

            for file_modified_at, file_path,file_hash in zip(fe.modified_at,fe.file_paths,fe.save_hashes):
                the_path = Path(file_path)
                game_name = the_path.parent.name
                game_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_game_id(game_name),self.loop)
                game_id = game_id_future.result()
                user_id = 1 # Hardcoded-__-
                    
                future = asyncio.run_coroutine_threadsafe(db_actions.insert_saves_created(game_id,user_id,file_modified_at,file_path,file_hash),self.loop)

                future.result()

                if verbose:
                    print("From FE:")
                    print(f"the_path: {the_path}")
                    print(f"game_name: {game_name}")
                    print(f"game_id: {game_id}")
                    print(f"Uploaded {the_path} - Creation to database")
                    print("------------------------------------------")       
        else:
            folder_path = Path(event.src_path).parent.name
            fe.explore_folder(Path(folder_path))
            if verbose:
                print("From FE:")
                print(f"Folder path passed in fe:{folder_path}")
                print(f"Folder created: {event.src_path}")
                print(f"Folder names: {fe.folder_names}")
                print(f"Folder paths: {fe.folder_paths}")
                print("------------------------------------------")  

            for folder_name in fe.folder_names:
                    
                future = asyncio.run_coroutine_threadsafe(db_actions.insert_games_created(folder_name),self.loop)

                future.result()
                if verbose:
                    print(f"From FE: folder_name: {folder_name}")
                    print(f"Uploaded {folder_name} - Creation in database")
                    print("------------------------------------------")

        fe.clear()
        print("Fe cleared!")
        print("------------------------------------------")

    def on_modified(self, event: FileSystemEvent, verbose = True):
        if not event.is_directory:
            fe.explore_file(Path(event.src_path))
            asyncio.run(upload(fe))
            if verbose:
                print(f"From FE: File modified: {event.src_path}")
                print("------------------------------------------")
            else:
                folder_path = Path(event.src_path).parent.name
                fe.explore_folder(Path(folder_path))
                if verbose:
                    print("From FE:")
                    print(f"Folder modified: {event.src_path}")
                    print(f"Folder names: {fe.folder_names}")
                    print(f"Folder paths: {fe.folder_paths}")
                    print("------------------------------------------") 

        for folder_name in fe.folder_names:
            game_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_game_id(folder_name),self.loop)
            game_id = game_id_future.result()

            future = asyncio.run_coroutine_threadsafe(db_actions.insert_games_modified(folder_name,game_id),self.loop)

            if verbose:
                print(f"Uploaded {folder_name} - Modified to database")

            future.result()
        
        for file_modified_at,file_path,file_hash in zip(fe.modified_at,fe.file_paths,fe.save_hashes):
            save_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_save_id(file_path),self.loop)
            save_id = save_id_future.result()

            future = asyncio.run_coroutine_threadsafe(db_actions.insert_saves_modified(save_id,file_modified_at,file_hash),self.loop)

            if verbose:
                print(f"Uploaded {file_path} - Modified to database")

            future.result()

        fe.clear()

    def on_moved(self, event: FileSystemEvent, verbose = True):
        if not event.is_directory:
            fe.explore_file(Path(event.dest_path))
            upload_status = asyncio.run(upload(fe))

            if upload_status:
                asyncio.run(delete_file(event.src_path))

            if verbose:
                print(f"file moved: {event.src_path} -> {event.dest_path}")

        else:
            folder_path = Path(event.dest_path).parent.name
            fe.explore_folder(Path(folder_path))
            upload_status = asyncio.run(upload(fe))

            if upload_status:
                asyncio.run(delete_folder(event.src_path))

            if verbose:
                print(f"Folder moved: {event.src_path} -> {event.dest_path}")
                print(f"Folder names: {fe.folder_names}")
                print(f"Folder paths: {fe.folder_paths}")
                print("------------------------------------------")

        for file_modified_at, file_path,file_hash in zip(fe.modified_at,fe.file_paths,fe.save_hashes):
            save_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_save_id(file_path),self.loop)
            save_id = save_id_future.result()

            future = asyncio.run_coroutine_threadsafe(db_actions.insert_saves_moved(save_id,file_modified_at,file_path,file_hash),self.loop)

            future.result()

        fe.clear()



    def on_deleted(self, event: FileSystemEvent, verbose = True):
        the_path = Path(event.src_path)
        if not event.is_directory:
            asyncio.run(delete_file(event.src_path))
            save_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_save_id(event.src_path),self.loop)
            save_id = save_id_future.result()
            future = asyncio.run_coroutine_threadsafe(db_actions.save_deleted(save_id),self.loop)
            future.result()
            if verbose:
                print(f"Deleted file: {event.src_path}")
                print("------------------------------------------")
        else:
            asyncio.run(delete_folder(event.src_path))
            game_name = the_path.name
            game_id_future = asyncio.run_coroutine_threadsafe(db_actions.get_game_id(game_name),self.loop)
            game_id = game_id_future.result()

            future = asyncio.run_coroutine_threadsafe(db_actions.game_deleted(game_id),self.loop)
            future.result()
            if verbose:
                print(f"Deleted folder: {event.src_path}")
                print("------------------------------------------")

        

class Worker:
    def __init__(self, loop):
        self.loop = loop
        self.observer = Observer()
        self.event_handler = TheEventHandler(loop=self.loop)
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
    Worker().the_start()

if __name__ == "__main__":
    main()