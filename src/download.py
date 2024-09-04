from time import perf_counter
from dotenv import load_dotenv
from datetime import datetime
import os
from cdse import CDSE
from shared import Shared
from schema.root_folders import RootFolders
from loguru import logger
from typing import List, Tuple, Dict

load_dotenv()


class Downloader:
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

    def download_data(self):
        api = self._login()
        api.set_collection("Sentinel2")
        api.set_processing_level("S2MSI2A")

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
        features_info, general_size, online_count = form_feature_data(features=features)


def main() -> None:
    shared: Shared = Shared()

    downloader: Downloader = Downloader(shared=shared)
    downloader.download_data()


if __name__ == "__main__":
    main()
