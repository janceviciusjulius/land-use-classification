import os
from typing import Optional, Dict, List
from venv import logger
from os import listdir

from domain.shared import Shared
from schema.folder_types import FolderType
from schema.metadata_types import Metadata


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
        cloud_percentages: Dict[str, float] = self.shared.read_json(path=self.files[Metadata.CLOUD_COVERAGE])
        files: List[str] = listdir(self.folders[FolderType.DOWNLOAD])
        logger.info(f"Merge process of the selected folder starts. Folders to merge: {len(files)}")

        for file in files:
            temp_working_dir_name: str = os.path.join(self.folders[FolderType.DOWNLOAD], file)
            self.shared.delete_all_xml(temp_working_dir_name)


            cloud_percentage: float = cloud_percentages[file]

            output_file_name = os.path.join(
                se,
                (str(i) + ". " + date + " " + str(files[i - 1]).split("_")[5] + " " + str(cloud_percentage) + "%.tiff"),
            )

    def _create_folders(self) -> None:
        self.shared.create_folder(path=self.folders[FolderType.MERGED])
        self.shared.create_folder(path=self.folders[FolderType.CLOUD])
        self.shared.create_folder(path=self.folders[FolderType.CLEANED])
