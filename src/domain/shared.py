import os
from json import dumps, load
from os.path import isdir
from shutil import rmtree
from typing import Dict, List, Optional
from zipfile import BadZipfile, ZipFile

from loguru import logger

from schema.folder_types import FolderPrefix, FolderType
from schema.parameters import Parameters
from schema.root_folders import RootFolders
from schema.yes_no import YesNo


class Shared:

    def __init__(self):
        self.root_folders = self.create_root_folders()

    @staticmethod
    def unzipping_data(source: str, destination: str):
        files: List[str] = os.listdir(source)
        if len(files) == 0:
            raise ValueError("No files to unzip.")

        logger.info(f"Data unzipping begins. Number of files: {len(files)}")
        for index, file in enumerate(files):
            try:
                temp_file_path = os.path.join(source, file)
                with ZipFile(temp_file_path, "r") as zip_ref:
                    zip_ref.extractall(destination)
                logger.info(f"Successfully unzipped {index + 1} file")
            except BadZipfile:
                logger.error(f"Due to downloaded file problem {index + 1} file is skipped.")
                continue
        logger.info("Unzipping complete.")

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
        current_dir: str = os.path.dirname(os.path.abspath(__file__))
        src_root: str = os.path.abspath(os.path.join(current_dir, os.pardir))
        parent: str = os.path.dirname(src_root)
        return parent

    def ask_deletion(self, folders: Dict[FolderType, str], scenario: FolderType) -> None:
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
        boolean: str = str(input("Some data already exists. Do you want to delete the data (Y/N)? "))

        if boolean.lower() == YesNo.YES:
            folders_to_delete: List[FolderType] = deletion_scenarios[scenario]
            for folder_to_delete in folders_to_delete:
                self.delete_folder(folders[folder_to_delete])
        else:
            logger.info("Data left on the disk.")

    @staticmethod
    def delete_folder(path: str):
        logger.info("Deletion of unnecessary data begins. ")
        try:
            rmtree(path)
            logger.info("Data deletion successful.")
        except (os.error, OSError, FileNotFoundError, NotADirectoryError):
            logger.error("Folder cannot be found. Skipping")

    def check_if_data_folder_exists(self, folders: Dict[FolderType, str], scenario: FolderType) -> str:
        if isdir(folders[scenario]):
            self.ask_deletion(folders=folders, scenario=scenario)
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

    @staticmethod
    def save_search_parameters(start_date: str, end_date: str, cloud_cover: str):
        data = {
            Parameters.START_DATE: start_date,
            Parameters.END_DATE: end_date,
            Parameters.CLOUD_COVERAGE: cloud_cover,
        }
