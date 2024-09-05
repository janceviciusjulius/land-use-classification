import os
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List, Tuple, Union, Optional

from dotenv import load_dotenv
from loguru import logger

from cdse import CDSE
from schema.root_folders import RootFolders
from schema.folder_types import FolderType, FolderTypePrefix
from shared import Shared

load_dotenv()


class Downloader:
    SENTINEL_COLLECTION: str = "Sentinel2"
    SENTINEL_PROCESSING_LEVEL: str = "S2MSI2A"
    B_to_GB = 1024 * 1024 * 1024

    ZEMAITIJA: List[str] = ["34UDG", "34VDH", "34UEG", "34VEH"]
    AUKSTAITIJA: List[str] = ["34VFH", "34UFG", "35VLC", "35ULB", "35UMB", "35VMC"]
    SUVALKAI: List[str] = ["34UFF", "34UFE", "35ULA", "34UGE"]
    DZUKAI: List[str] = ["35ULV", "35UMA", "35UMV"]
    FOOTPRINT: List[str] = ZEMAITIJA + AUKSTAITIJA + SUVALKAI + DZUKAI

    def __init__(self, shared: Shared):
        self.shared = shared
        self.root_folders = self.shared.create_root_folders()
        self.interpolation = None
        self.start_date = None
        self.end_date = None
        self.max_cloud_cover = None
        self.folders = {}

    def download_data(self):
        api = self._login()
        api.set_collection(self.SENTINEL_COLLECTION)
        api.set_processing_level(self.SENTINEL_PROCESSING_LEVEL)

        self._generate_parameters(api=api)
        main_folder_path = os.path.join(
            self.root_folders[RootFolders.DATA_FOLDER], self._generate_folder_name()
        )
        self.folders[FolderType.PARENT] = self.shared.create_folder(
            path=main_folder_path
        )
        self.check_if_data_folder_exists(folder_type_prefix=FolderTypePrefix.DOWNLOAD)


    def check_if_data_folder_exists(self, folder_type_prefix: FolderTypePrefix):
        folder_path: str = os.path.join(
            self.folders[FolderType.PARENT],
            self.shared.generate_folder_name(
                start_date=self.start_date,
                end_date=self.end_date,
                max_cloud_cover=self.max_cloud_cover,
                folder_type=folder_type_prefix,
            ),
        )


        print(folder_path)

    def _generate_parameters(self, api):
        download_process: bool = False
        while not download_process:
            self._set_time_interval()
            self._set_max_cloud_cover()

            footprint = CDSE.process_footprint(self.FOOTPRINT)
            features = api.query(
                start_date=self.start_date,
                end_date=self.end_date,
                footprint=footprint,
                cloudcover=self.max_cloud_cover,
                max_records=None,
            )

            features_info, general_size, online_count = self._form_feature_data(
                features=features
            )
            if len(features_info) == 0:
                logger.error(
                    "No data was found according to the given criteria. Please try again."
                )
            else:
                download_process = True

    @staticmethod
    def _login() -> CDSE:
        logger.info("Sentinel-2 satellite data download algorithm.")
        logger.info("Loading user from .env")
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")
        return CDSE((username, password))

    def _set_time_interval(self):
        start_time = input("Specify a search start date (YYYY-MM-DD): ")
        end_time = input("Specify a search finish date (YYYY-MM-DD): ")
        while (
            (end_time < start_time)
            or (end_time > datetime.now().strftime("%Y-%m-%d"))
            or (len(start_time) != 10)
            or (len(end_time) != 10)
        ):
            self.shared.clear_console()
            logger.error("Bad interval. Please re-enter the date:\n")
            start_time = input("Specify a search start date (YYYY-MM-DD): ")
            end_time = input("Specify a search finish date (YYYY-MM-DD): ")
        self.shared.clear_console()
        self.start_date = start_time
        self.end_date = end_time

    def _set_max_cloud_cover(self):
        while True:
            try:
                max_cloud_cover = int(
                    input("Specify a maximum percentage of cloud cover (0%-100%): ")
                )
                while not (0 <= max_cloud_cover <= 100):
                    self.shared.clear_console()
                    logger.error(
                        "The specified maximum cloud percentage is out of range or is smaller than minimum range."
                    )
                    max_cloud_cover = int(
                        input("Specify a maximum percentage of cloud cover (0%-100%):")
                    )
                self.max_cloud_cover = max_cloud_cover
            except ValueError:
                self.shared.clear_console()
                logger.error("Invalid input format.")
                continue
            else:
                break
        self.shared.clear_console()

    def _form_feature_data(
        self, features
    ) -> Tuple[Dict[str, Any], Union[int, float], int]:
        feature_info: Dict[str, Any] = {}
        general_size: Union[int, float] = 0
        online_num: int = 0

        for index, feature in enumerate(features):
            if feature["properties"]["status"].lower() == "online":
                online_num += 1

            title = feature["properties"]["title"]
            feature_size = round(
                feature["properties"]["services"]["download"]["size"] / self.B_to_GB, 2
            )
            general_size += feature_size
            feature_info[title] = {
                "Title": title,
                "Date": feature["properties"]["startDate"][:10].replace("-", ""),
                "Status": feature["properties"]["status"],
                "Size": feature_size,
                "CloudCover": round(feature["properties"]["cloudCover"], 2),
                "Coordinates": feature["geometry"]["coordinates"],
                "QMLGeometry": feature["properties"]["gmlgeometry"],
            }

        return feature_info, round(general_size, 2), online_num


def main() -> None:
    shared: Shared = Shared()

    downloader: Downloader = Downloader(shared=shared)
    downloader.download_data()


if __name__ == "__main__":
    main()
