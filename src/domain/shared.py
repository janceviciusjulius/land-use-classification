import os
import sys
from enum import Enum
from json import dump, load
from os.path import isdir
from shutil import rmtree
from typing import Any, Dict, List, Optional, Tuple, Union
from zipfile import BadZipfile, ZipFile
from tkinter import filedialog

from loguru import logger

from schema.constants import Constants
from schema.file_modes import FileMode
from schema.file_types import FileType
from schema.folder_types import FolderPrefix, FolderType
from schema.metadata_types import CloudCoverageJson, ParametersJson
from schema.root_folders import RootFolders
from schema.yes_no import YesNo


class Shared:
    PARAMETERS_FILENAME = "parameters.json"
    INFORMATION_FILENAME = "information.json"

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
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        return path

    def create_root_folders(self) -> Dict[RootFolders, str]:
        root_folders: Dict[type(RootFolders), str] = {}
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

    def choose_files_from_folder(self) -> List[str]:
        self.clear_console()
        logger.info(f"Data joining/cropping algorithm")
        logger.info("Please choose file/files which You want to join/crop")
        files_paths = list(filedialog.askopenfilenames(initialdir=self.root_folders[RootFolders.DATA_FOLDER]))
        return files_paths

    def choose_shp_from_folder(self) -> str:
        logger.info("Please choose .shp file for cropping...")
        filetypes: Tuple[Tuple[str, str], ...] = (("ESRI Shapefile", "*.shp"), ("GeoPackage", "*.gpkg"))
        shp_path: str = filedialog.askopenfilename(
            initialdir=self.root_folders[RootFolders.SHP_FOLDER], filetypes=filetypes
        )
        return shp_path

    @staticmethod
    def convert_key_to_enum(key: str, enum_class: type(Enum)) -> Union[str, type(Enum)]:
        try:
            return enum_class(key)
        except ValueError:
            return key

    def get_parameters(self, files_paths: List[str]) -> Dict[Any, Any]:
        file_path, *_ = files_paths
        json_file_path: str = os.path.join(os.path.dirname(os.path.dirname(file_path)), self.PARAMETERS_FILENAME)
        data: Dict[str, Any] = self.read_json(json_file_path)
        del data[ParametersJson.FILES]
        return self._convert_json_to_enum(data=data, param_enum=ParametersJson, folder_enum=FolderType)

    def _convert_json_to_enum(self, data, param_enum, folder_enum):
        result = {}
        for key, value in data.items():
            new_key = self.convert_key_to_enum(key, param_enum)
            if isinstance(value, dict):
                if new_key == param_enum.FOLDERS:
                    value = self._convert_json_to_enum(value, folder_enum, folder_enum)
                else:
                    value = self._convert_json_to_enum(value, param_enum, folder_enum)
            result[new_key] = value
        return result

    @staticmethod
    def display_options(options: List[str]):
        logger.info("Select cutting layer:")
        for i, option in enumerate(options, 1):
            print(f"     {i}. {option}")

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

    def validate_json(self, json_data: Dict[Any, Any]):
        pass

    def to_dict(self, cls_obj: Any) -> Dict[str, Any]:
        dict_: [Any, Any] = cls_obj.__dict__.copy()
        dict_.pop("shared", None)
        return self._convert_enum_keys(dict_)

    @staticmethod
    def dumb_to_json(path: str, data: Dict[str, Any]):
        with open(path, FileMode.WRITE) as f:
            dump(data, f, indent=4)

    @staticmethod
    def read_json(path: str) -> Dict[str, Any]:
        with open(path, FileMode.READ) as file:
            data_dict = load(file)
        return data_dict

    def update_information(self, folder: str, json_file_path: str):
        data: Dict[str, Dict[str, Any]] = self.read_json(path=json_file_path)

        for file_id, file_details in data.items():
            date: str = file_details[CloudCoverageJson.DATE]
            tile: str = file_details[CloudCoverageJson.TILE]
            cloud: str = str(file_details[CloudCoverageJson.CLOUD])

            match_file_name: str = self._match_file_with_criteria(folder=folder, date=date, tile=tile, cloud=cloud)
            file_details[CloudCoverageJson.FILENAME.value] = match_file_name
        self.dumb_to_json(data=data, path=json_file_path)

    @staticmethod
    def _match_file_with_criteria(folder: str, date: str, tile: str, cloud: str) -> Optional[str]:
        files_in_folder: List[str] = os.listdir(folder)
        for file in files_in_folder:
            if date in file and tile in file and str(cloud) in file:
                return os.path.join(folder, file)
        return None

    @staticmethod
    def delete_all_xml(dir_name):
        delete_xml = [
            band for band in os.listdir(dir_name) if band.endswith(FileType.XML) and not band.startswith(FileType.MTD)
        ]
        for xml in delete_xml:
            os.remove(os.path.join(dir_name, xml))

    @staticmethod
    def rename_file(path: str, old_prefix: str, new_prefix: str) -> str:
        file_name: str = os.path.basename(path)
        path_without_filename: str = os.path.dirname(path)
        new_file_name: str = file_name.replace(old_prefix, new_prefix)
        return os.path.join(path_without_filename, new_file_name)

    @staticmethod
    def get_shp_from_path(path: str) -> Optional[str]:
        if path:
            file_name: str = os.path.basename(path)
            if FileType.GPKG in file_name:
                return file_name.replace(FileType.GPKG, Constants.EMPTY_STRING)
            return file_name.replace(FileType.SHP, Constants.EMPTY_STRING)
        return None


    @staticmethod
    def progress_cb(complete, message, cb_data):
        if int(complete * 100) % 10 == 0:
            print(f"{complete * 100:.0f}", end="", flush=True)
        elif int(complete * 100) % 3 == 0:
            print(f"{cb_data}", end="", flush=True)
        if int(complete * 100) == 100:
            print(f"", end=" - done.\n", flush=True)
