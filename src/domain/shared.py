import os
import sys
from enum import Enum
from json import dump, load
from os.path import isdir
from shutil import rmtree
from typing import Dict, List, Optional, Any
from zipfile import BadZipfile, ZipFile

from loguru import logger

from schema.folder_types import FolderPrefix, FolderType
from schema.parameters import Parameters
from schema.root_folders import RootFolders
from schema.yes_no import YesNo


class Shared:
    PARAMETERS_FILENAME = "parameters.json"
    CLOUD_COVER_FILENAME = "cloud_coverage.json"

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
            sys.exit(1)

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

    @staticmethod
    def get_value(obj: Any, value: str) -> Any:
        return getattr(obj, value)

    def generate_folders(self, start_date, end_date, cloud_cover) -> Dict[FolderType, str]:
        folders: Dict[FolderType, str] = {}

        folder_mapping: Dict[FolderType, Optional[FolderPrefix]] = {
            FolderType.PARENT: None,
            FolderType.DOWNLOAD: FolderPrefix.DOWNLOAD,
            FolderType.ZIP: FolderPrefix.ZIP,
            FolderType.MOVED: FolderPrefix.MOVED,
            FolderType.MERGED: FolderPrefix.MERGED,
            FolderType.CLEANED: FolderPrefix.CLEANED,
            FolderType.CLOUD: FolderPrefix.CLOUD,
            FolderType.JOINED: FolderPrefix.JOINED,
            FolderType.CLASSIFIED: FolderPrefix.CLASSIFIED,
        }

        main_folder_name = self.generate_folder_name(start_date, end_date, cloud_cover)
        main_folder_path = os.path.join(self.root_folders[RootFolders.DATA_FOLDER], main_folder_name)
        folders[FolderType.PARENT] = main_folder_path

        for folder_type, prefix in folder_mapping.items():
            if folder_type != FolderType.PARENT:
                folder_name = self.generate_folder_name(start_date, end_date, cloud_cover, prefix)
                folder_path = os.path.join(main_folder_path, folder_name)
                folders[folder_type] = folder_path
        return folders

    def _convert_enum_keys(self, dict_: Dict[Any, Any]) -> Dict[Any, Any]:
        if isinstance(dict_, dict):
            return {
                key.name if isinstance(key, Enum) else key: self._convert_enum_keys(value)
                for key, value in dict_.items()
            }
        else:
            return dict_

    # TODO: ADD READING JSON SUPPORT
    # @staticmethod
    # def _load_json_with_enum(json_str: str, enum_type: Enum) -> Dict[str, Any]:
    #     data = loads(json_str)
    #
    #     if 'folders' in data:
    #         data['folders'] = {enum_type[key]: value for key, value in data['folders'].items()}
    #
    #     return data

    def to_dict(self, cls_obj: Any) -> Dict[str, Any]:
        dict_: [Any, Any] = cls_obj.__dict__.copy()
        dict_.pop("shared", None)
        return self._convert_enum_keys(dict_)

    @staticmethod
    def dumb_to_json(path: str, data: Dict[str, Any]):
        with open(path, "w") as f:
            dump(data, f, indent=4)

    @staticmethod
    def read_json(path: str) -> Dict[str, Any]:
        with open(path, "r") as file:
            data_dict = load(file)
        return data_dict

    def generate_folders(self):
