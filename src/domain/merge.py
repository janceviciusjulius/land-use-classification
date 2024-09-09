import os
from typing import Optional, Dict, List
from venv import logger
from os import listdir

from domain.shared import Shared
from schema.folder_types import FolderType
from schema.metadata_types import Metadata, ParametersJson, CloudCoverageJson


# TODO: CONTINUE WORKING ON MERGE REFACTORING
class Merge:
    GDAL_MERGE: str = "gdal_merge.py"

    def __init__(
        self,
        shared: Shared,
        interpolation: bool,
        start_date: str,
        end_date: str,
        max_cloud_cover: int,
        folders: [Dict[FolderType, str]],
        files: Dict[str | Metadata, str],
    ):
        self.shared: Shared = shared
        self.interpolation: bool = interpolation
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.max_cloud_cover: int = max_cloud_cover
        self.folders: [Dict[FolderType, str]] = folders
        self.files: Dict[str | Metadata, str] = files

    def process_data(self):
        logger.info("Starting merging...")
        self._create_folders()
        self._merge()

    def _merge(self):
        files_information: Dict[str, float] = self.shared.read_json(path=self.files[Metadata.CLOUD_COVERAGE])
        files: List[str] = listdir(self.folders[FolderType.DOWNLOAD])
        logger.info(f"Merge process of the selected folder starts. Folders to merge: {len(files)}")

        for index, file in enumerate(files):
            temp_working_dir_name: str = os.path.join(self.folders[FolderType.DOWNLOAD], file)
            self.shared.delete_all_xml(temp_working_dir_name)

            cloud_percentage: float = files_information[file][CloudCoverageJson.CLOUD]
            date: str = files_information[file][CloudCoverageJson.DATE]
            tile: str = files_information[file][CloudCoverageJson.TILE]

            out_filename: str = os.path.join(
                self.folders[FolderType.MERGED], f"{index+1}. {date} {tile} {cloud_percentage}%.tiff"
            )

            cloud_10_filename: str = os.path.join(
                self.folders[FolderType.CLOUD], f"{index+1}. Cloud {date} {tile} {cloud_percentage}%.tiff"
            )

            cloud_20_filename = os.path.join(
                self.folders[FolderType.CLOUD], f"{index+1}. Cloud {date} {tile} {cloud_percentage}%_20m.tiff"
            )

    def _create_folders(self) -> None:
        self.shared.create_folder(path=self.folders[FolderType.MERGED])
        self.shared.create_folder(path=self.folders[FolderType.CLOUD])
        self.shared.create_folder(path=self.folders[FolderType.CLEANED])
