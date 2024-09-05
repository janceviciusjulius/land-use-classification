import os
import shutil
from os.path import isdir
from typing import Dict, List, Optional, Tuple

from tensorboard.backend.event_processing.data_provider import logger

from schema.folder_types import FolderPrefix, FolderType
from schema.root_folders import RootFolders
from schema.yes_no import YesNo


class Shared:

    def __init__(self):
        self.root_folders = self.create_root_folders()

    @staticmethod
    def create_folder(path: str) -> str:
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
        folder_type: Optional[FolderPrefix] = None,
    ) -> str:
        name = start_date + ".." + end_date + " " + "0" + "-" + str(max_cloud_cover) + "%"
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

    def ask_deletion(self, folders: Dict[FolderType, str], scenario: FolderType) -> str:
        deletion_scenarios: Dict[FolderType, List[FolderType]] = {
            FolderType.DOWNLOAD: [
                FolderType.DOWNLOAD,
                FolderType.ZIP,
                FolderType.CLEANED,
                FolderType.MERGED,
                FolderType.CLOUD,
            ],
            FolderType.PARENT: [FolderType.PARENT],
        }

        logger.info("NOTE: All downloaded and pre-processed data will be deleted.")
        boolean: str = str(input("Do you want to delete the data (Y/N)? "))

        if boolean.lower() == YesNo.YES:
            folders_to_delete: List[FolderType] = deletion_scenarios[scenario]
            for folder_to_delete in folders_to_delete:
                print(folders[folder_to_delete])
                self.delete_folder(folders[folder_to_delete])

    @staticmethod
    def delete_folder(path: str):
        logger.info("Deletion of unnecessary data begins. ")
        try:
            shutil.rmtree(path)
            logger.info("Data deletion successful.")
        except (os.error, OSError, FileNotFoundError, NotADirectoryError):
            logger.error("Folder cannot be found. Skipping")

    def check_if_data_folder_exists(self, folders: Dict[FolderType, str], scenario: FolderType) -> str:
        if isdir(folders[scenario]):
            print("EINU I DELETE")
            return self.ask_deletion(folders=folders, scenario=scenario)

        path = self.create_folder(path=folders[scenario])
        return path

    def create_parent_folder(self, folders):
        if isdir(folders[FolderType.PARENT]):
            self.ask_deletion(folders=folders, scenario=FolderType.PARENT)
        return self.create_folder(path=folders[FolderType.PARENT])

    def generate_folders(self, start_date, end_date, cloud_cover) -> Dict[FolderType, str]:
        folders: Dict[FolderType, str] = {}

        main_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover)
        download_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.DOWNLOAD)
        zip_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.ZIP)
        moved_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.MOVED)
        merged_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.MERGED)
        cleaned_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.CLEANED)
        cloud_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.CLOUD)
        joined_folder_name: str = self.generate_folder_name(start_date, end_date, cloud_cover, FolderPrefix.JOINED)
        classified_folder_name: str = self.generate_folder_name(
            start_date, end_date, cloud_cover, FolderPrefix.CLASSIFIED
        )

        main_folder_path: str = os.path.join(self.root_folders[RootFolders.DATA_FOLDER], main_folder_name)
        download_folder_path: str = os.path.join(main_folder_path, download_folder_name)
        zip_folder_path: str = os.path.join(main_folder_path, zip_folder_name)
        moved_folder_path: str = os.path.join(main_folder_path, moved_folder_name)
        merged_folder_path: str = os.path.join(main_folder_path, merged_folder_name)
        cleaned_folder_path: str = os.path.join(main_folder_path, cleaned_folder_name)
        cloud_folder_name: str = os.path.join(main_folder_path, cloud_folder_name)
        joined_folder_path: str = os.path.join(main_folder_path, joined_folder_name)
        classified_folder_path: str = os.path.join(main_folder_path, classified_folder_name)

        folders[FolderType.PARENT] = main_folder_path
        folders[FolderType.DOWNLOAD] = download_folder_path
        folders[FolderType.ZIP] = zip_folder_path
        folders[FolderType.MOVED] = moved_folder_path
        folders[FolderType.MERGED] = merged_folder_path
        folders[FolderType.CLEANED] = cleaned_folder_path
        folders[FolderType.CLOUD] = cloud_folder_name
        folders[FolderType.JOINED] = joined_folder_path
        folders[FolderType.CLASSIFIED] = classified_folder_path
        return folders
