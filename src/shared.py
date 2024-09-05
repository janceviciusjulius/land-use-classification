import os
import shutil
from os.path import isdir
from typing import Dict, Optional, Tuple

from tensorboard.backend.event_processing.data_provider import logger

from schema.root_folders import RootFolders
from schema.folder_types import FolderTypePrefix


class Shared:

    def __init__(self):
        self.root_folders = self.create_root_folders()

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

    def ask_deletion(self, folder_path: str):
        logger.info("NOTE: All downloaded and pre-processed data will be deleted.")
        boolean = str(input("Do you want to delete the data (Y/N)? "))
        if boolean.lower() == "y":
            raw_data_folder = (
                    "Sentinel2 "
                    + start_time
                    + ".."
                    + end_time
                    + " "
                    + "0"
                    + "-"
                    + str(max_cloud_cover)
                    + "%"
            )
            if os.path.exists(
                    os.path.join(main_folder_path, "Cleaned " + raw_data_folder)
            ):
                shutil.rmtree(
                    os.path.join(main_folder_path, "Cleaned " + raw_data_folder)
                )
            if os.path.exists(
                    os.path.join(main_folder_path, "Merged " + raw_data_folder)
            ):
                shutil.rmtree(
                    os.path.join(main_folder_path, "Merged " + raw_data_folder)
                )
            if os.path.exists(
                    os.path.join(main_folder_path, "Cloud " + raw_data_folder)
            ):
                shutil.rmtree(
                    os.path.join(main_folder_path, "Cloud " + raw_data_folder)
                )
            self.delete_folder(os.path.join(main_folder_path, raw_data_folder))

    @staticmethod
    def delete_folder(path: str):
        logger.info("Deletion of unnecessary data begins. ")
        try:
            shutil.rmtree(path)
            logger.info("Data deletion successful.")
        except (os.error, OSError, FileNotFoundError, NotADirectoryError):
            logger.error("Data deletion error.")


    def check_if_data_folder_exists(
        self,
        folder: str,
        start_date: str,
        end_date: str,
        max_cloud_cover: int,
        folder_type_prefix: FolderTypePrefix,
    ) -> Tuple[bool, str]:
        folder_path = os.path.join(
            folder,
            self.generate_folder_name(
                start_date=start_date,
                end_date=end_date,
                max_cloud_cover=max_cloud_cover,
                folder_type=folder_type_prefix,
            ),
        )
        if isdir(folder_path):
            # TODO: ask to delete
            return True, folder_path
        self.create_folder(folder_path)
        return False, folder_path
