import os
from datetime import datetime
from os.path import isdir
from time import perf_counter
from typing import Any, Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from loguru import logger

from cdse import CDSE
from schema.downloader_info import DownloadInfo
from schema.folder_types import FolderPrefix, FolderType
from schema.root_folders import RootFolders
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
        self.shared: Shared = shared
        self.interpolation: Optional[bool] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        self.max_cloud_cover: Optional[int] = None
        self.folders: Dict[FolderType, str] = {}

    def download_data(self):
        api = self._login()
        info: Dict[str, Any] = self._generate_parameters(api=api)

        self.folders: Dict[FolderType, str] = self.shared.generate_folders(
            start_date=self.start_date,
            end_date=self.end_date,
            cloud_cover=self.max_cloud_cover,
        )

        self.shared.check_if_data_folder_exists(folders=self.folders, scenario=FolderType.DOWNLOAD)

        # if download_folder_exists:
        #     self.shared.ask_deletion(folder_path=download_folder_path)
        # self._request_analysis(
        #         files=info[DownloadInfo.FEATURES_INFO],
        #         size=info[DownloadInfo.GENERAL_SIZE],
        #         available_count=info[DownloadInfo.ONLINE_COUNT],
        #     )

    @staticmethod
    def _request_analysis(files, size, available_count):
        logger.info(f"Data files found: {len(files)}")
        logger.info(f"Size of the files: {size} GB")
        logger.info(
            f"Of the {len(files)} files, {available_count} are active and available,"
            f" {len(files) - available_count} are currently unavailable."
        )
        logger.info(
            "NOTE: Unavailable data may become available during data download. If this happens, the data will be "
            "downloaded."
        )

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

            features_info, general_size, online_count = self._form_feature_data(features=features)
            if len(features_info) == 0:
                logger.error("No data was found according to the given criteria. Please try again.")
            else:
                download_process = True
        return {
            "features_info": features_info,
            "general_size": general_size,
            "online_count": online_count,
        }

    def _login(self) -> CDSE:
        logger.info("Sentinel-2 satellite data download algorithm.")
        logger.info("Loading user from .env")
        username: str = os.environ.get("USERNAME")
        password: str = os.environ.get("PASSWORD")

        api: CDSE = CDSE((username, password))
        api.set_collection(self.SENTINEL_COLLECTION)
        api.set_processing_level(self.SENTINEL_PROCESSING_LEVEL)
        return api

    def _set_time_interval(self):
        start_time = input("Specify a search start date (YYYY-MM-DD): ")
        end_time = input("Specify a search finish date (YYYY-MM-DD): ")
        while (
            (end_time < start_time)
            or (end_time > datetime.now().strftime("%Y-%m-%d"))
            or (len(start_time) != 10)
            or (len(end_time) != 10)
        ):
            # self.shared.clear_console()
            logger.error("Bad interval. Please re-enter the date:\n")
            start_time = input("Specify a search start date (YYYY-MM-DD): ")
            end_time = input("Specify a search finish date (YYYY-MM-DD): ")
        # self.shared.clear_console()
        self.start_date = start_time
        self.end_date = end_time

    def _set_max_cloud_cover(self):
        while True:
            try:
                max_cloud_cover = int(input("Specify a maximum percentage of cloud cover (0%-100%): "))
                while not (0 <= max_cloud_cover <= 100):
                    # self.shared.clear_console()
                    logger.error(
                        "The specified maximum cloud percentage is out of range or is smaller than minimum range."
                    )
                    max_cloud_cover = int(input("Specify a maximum percentage of cloud cover (0%-100%):"))
                self.max_cloud_cover = max_cloud_cover
            except ValueError:
                # self.shared.clear_console()
                logger.error("Invalid input format.")
                continue
            else:
                break
        # self.shared.clear_console()

    def _form_feature_data(self, features) -> Tuple[Dict[str, Any], Union[int, float], int]:
        feature_info: Dict[str, Any] = {}
        general_size: Union[int, float] = 0
        online_num: int = 0

        for index, feature in enumerate(features):
            if feature["properties"]["status"].lower() == "online":
                online_num += 1

            title = feature["properties"]["title"]
            feature_size = round(feature["properties"]["services"]["download"]["size"] / self.B_to_GB, 2)
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
