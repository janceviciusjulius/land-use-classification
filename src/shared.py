import os
from os.path import isdir
from typing import Dict, Optional

from schema.root_folders import RootFolders
from src.schema.folder_types import FolderTypePrefix


class Shared:

    @staticmethod
    def create_folder(path: str) -> str:
        if not isdir(path):
            os.mkdir(path)
        return path

    def create_root_folders(self) -> Dict[RootFolders, str]:
        root_folders: Dict[RootFolders, str] = {}
        for root_folder in RootFolders:
            path = os.path.join(self._get_project_folder(), root_folder)
            root_folders[root_folder] = path
            if not isdir(path):
                os.mkdir(path)
        return root_folders

    @staticmethod
    def generate_folder_name(
        start_date: str,
        end_date: str,
        max_cloud_cover: int,
        folder_type: Optional[FolderTypePrefix] = None,
    ) -> str:
        name = (
            start_date + ".." + end_date + " " + "0" + "-" + str(max_cloud_cover) + "%"
        )
        if not folder_type:
            return name
        return folder_type + " " + name

    @staticmethod
    def clear_console():
        command = "clear"
        if os.name in ("nt", "dos"):
            command = "cls"
        os.system(command)

    @staticmethod
    def _get_project_folder() -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
        return project_root
