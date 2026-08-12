import hashlib
import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


class FileExplorer:
    def __init__(self):
        self.folder_paths = []
        self.folder_names = []
        self.file_paths = []
        self.file_names = []
        self.file_data = []
        self.file_type = []
        self.save_hashes = []
        self.modified_at = []
    
    def _content_type(self, path: Path):
        content_type, _ = mimetypes.guess_type(path)

        if content_type is None:
            content_type = "data file"
        
        return content_type
    
    def explore_file(self, file_path: Path):
        content_type = self._content_type(file_path)
        self.file_type.append(content_type)
        self.file_paths.append(str(file_path))
        self.file_names.append(file_path.name)
        self.modified_at.append(str(datetime.fromtimestamp(file_path.stat().st_mtime)))
        with file_path.open("rb") as file:
            data = file.read()
        self.file_data.append(data)
        self.save_hashes.append(hashlib.sha256(data).hexdigest())    

    
    def explore_folder(self,master_folder: Path):
        for folder in master_folder.rglob("*"):
            if folder.is_dir():
                self.folder_paths.append(str(folder))
                self.folder_names.append(folder.name)
            elif folder.is_file():
                self.explore_file(folder)
    
    def clear(self):
        self.folder_paths = []
        self.folder_names = []
        self.file_paths = []
        self.file_names = []
        self.file_data = []
        self.file_type = []
        self.save_hashes = []
        self.modified_at = []

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
    print(f"File names: {fe.file_names}")
    print(f"File content: {fe.file_data}" )
    print(f"File type: {fe.file_type} ")
    print(f"Folder names: {fe.folder_names}")
    print(f"Save hashes: {fe.save_hashes}")

if __name__ == "__main__":
    main()
                
