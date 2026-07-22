from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import os
import json

class FileExplorer():
    def __init__(self):
        self.folder_paths = []
        self.file_paths = []
        self.folder_names = []
        self.save_hashes = []
        self.modified_at = []
    
    def find_path(self,master_folder: Path):
        for folder in master_folder.rglob("*"):
            if folder.is_dir():
                self.folder_paths.append(str(folder))
                self.folder_names.append(folder.name)
            elif folder.is_file():
                self.file_paths.append(str(folder))
                self.modified_at.append(str(datetime.fromtimestamp(folder.stat().st_mtime)))
                with folder.open("rb") as file:
                    data = file.read()
                self.save_hashes.append(hashlib.sha256(data).hexdigest())

def main():
    load_dotenv()
    config_path = os.getenv("CONFIG")

    if os.path.exists(config_path):
        with open(config_path,"r") as f:
            config = json.load(f)
        print(config)
    else:
        return ("Config doesn't exists!")

    fe = FileExplorer()
    fe.find_path(Path(config["path"]))

    print(f"File paths: {fe.file_paths}")
    print(f"Folder names: {fe.folder_names}")
    print(f"Save hashes: {fe.save_hashes}")

if __name__ == "__main__":
    main()
                
