import os
from datetime import datetime
from io import BytesIO
from shutil import copyfile, rmtree
from sys import exit
from time import sleep
from typing import Any, Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from folium import GeoJson, Map
from geopandas import GeoDataFrame, GeoSeries
from loguru import logger
from pandas import DataFrame
from PIL import Image
from shapely import wkt
from tqdm import tqdm

from additional.cdse import CDSE
from additional.logger_configuration import configurate_logger
from domain.shared import Shared
from schema.downloader_info import DownloadInfo
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.metadata_types import CloudCoverageJson, Metadata
from schema.s2_package_content import PackageContent
from schema.yes_no import YesNo

configurate_logger()
load_dotenv()


class Downloader:
    SENTINEL_COLLECTION: str = "Sentinel2"
    SENTINEL_PROCESSING_LEVEL: str = "S2MSI2A"
    B_to_GB: int = 1024 * 1024 * 1024

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
        self.folders: Optional[Dict[FolderType, str]] = None
        self.files: Dict[str | Metadata, str] = {}

    def download_data(self):
        self.shared.clear_console()
        api = self._login()
        info: Dict[DownloadInfo, Any] = self._generate_parameters(api=api)

        self.folders: Dict[FolderType, str] = self.shared.generate_folders(
            start_date=self.start_date,
            end_date=self.end_date,
            cloud_cover=self.max_cloud_cover,
        )
        self.shared.create_parent_folder(folders=self.folders)
        self.shared.check_if_data_folder_exists(folders=self.folders, scenario=FolderType.DOWNLOAD)

        self._create_image_for_area_covered(
            search_result=info[DownloadInfo.FEATURES_INFO],
            dir_path=self.folders[FolderType.PARENT],
        )
        self._download_all(api=api, info=info)
        self.save_search_parameters()

    def _download_all(self, api: CDSE, info: Dict[DownloadInfo, Any]):
        while True:
            boolean = input("Do you want to download the data (Y/N)? ")
            if boolean.lower() == YesNo.YES:
                self.interpolation = self._ask_for_interpolation()
                logger.info("Starting downloading...")
                downloaded_list = api.download_features(
                    feature_list=info[DownloadInfo.FEATURES],
                    dir=self.folders[FolderType.DOWNLOAD],
                )
                sleep(0.5)
                self.files[Metadata.CLOUD_COVERAGE] = self.save_downloaded_files_id(
                    features=info[DownloadInfo.FEATURES_INFO]
                )
                self.log_downloaded_files(info=info, downloaded_list=downloaded_list)
                self.shared.unzipping_data(
                    source=self.folders[FolderType.DOWNLOAD],
                    destination=self.folders[FolderType.ZIP],
                )
                self.shared.delete_folder(path=self.folders[FolderType.DOWNLOAD])
                sleep(0.5)
                self.shared.create_folder(path=self.folders[FolderType.DOWNLOAD])
                self._unpack_s2_bands(
                    source=self.folders[FolderType.ZIP],
                    destination=self.folders[FolderType.DOWNLOAD],
                )
                self.shared.delete_folder(path=self.folders[FolderType.ZIP])
                break
            elif boolean.lower() == YesNo.NO:
                logger.info("The data download phase is skipped.")
                if len(os.listdir(self.folders[FolderType.PARENT])) == 2:
                    rmtree(self.folders[FolderType.PARENT])
                else:
                    rmtree(self.folders[FolderType.DOWNLOAD])
                exit(1)
            else:
                logger.error("Error. Please specify an answer.")

    def save_search_parameters(self) -> str:
        json_file_path: str = os.path.join(self.folders[FolderType.PARENT], self.shared.PARAMETERS_FILENAME)
        self.files[Metadata.PARAMETERS] = json_file_path

        class_variables: Dict[str, Any] = self.shared.to_dict(cls_obj=self)

        self.shared.dumb_to_json(path=json_file_path, data=class_variables)
        return json_file_path

    @staticmethod
    def _unpack_s2_bands(source, destination):
        files: List[str] = os.listdir(source)
        pbar: tqdm = tqdm(range(len(files)), desc="Unpacking S2 bands", unit="package")
        for i in pbar:
            pbar.set_description(f"Unpacking {i+1} file")
            temp_band_folder: str = os.path.join(destination, files[i])
            os.mkdir(temp_band_folder)

            dir_path: str = os.path.join(source, files[i])
            dir_files: List[str] = os.listdir(dir_path)
            for dir_file in dir_files:
                if dir_file.startswith("MTD") and dir_file.endswith(FileType.XML):
                    copyfile(
                        os.path.join(dir_path, dir_file),
                        os.path.join(temp_band_folder, dir_file),
                    )
            # End of XML part
            folder: str = os.path.join(source, files[i], PackageContent.GRANULE)
            data_name: List[str] = os.listdir(folder)
            folder: str = os.path.join(folder, data_name[0], PackageContent.IMG_DATA)
            img_data: List[str] = os.listdir(folder)
            if len(img_data) != 3:
                for j in range(len(img_data)):
                    band: str = os.path.join(folder, img_data[j])
                    temp_band_folder: str = os.path.join(destination, files[i], img_data[j])
                    copyfile(band, temp_band_folder)
            elif len(img_data) == 3:
                folders: List[str] = os.listdir(folder)
                for j in range(len(folders)):
                    path_to_folders: str = os.path.join(folder, folders[j])
                    img_data: List[str] = os.listdir(path_to_folders)
                    for z in range(len(img_data)):
                        band: str = os.path.join(path_to_folders, img_data[z])
                        temp_band_folder: str = os.path.join(destination, files[i], img_data[z])
                        copyfile(band, temp_band_folder)
        logger.info("Band exclusion complete.")

    @staticmethod
    def log_downloaded_files(info: Dict[DownloadInfo, Any], downloaded_list: List[Any]):
        logger.info(
            f"Data download complete. Of the {len(info[DownloadInfo.FEATURES])} files, {len(downloaded_list)}"
            f" were downloaded."
        )
        logger.info(
            f"Due to the server errors {len(info[DownloadInfo.FEATURES]) - len(downloaded_list)}"
            f" files could not be downloaded."
        )

    def save_downloaded_files_id(self, features: Dict[str, Any]) -> str:
        path: str = os.path.join(self.folders[FolderType.PARENT], self.shared.INFORMATION_FILENAME)
        data: Dict[str, Any] = {}
        for feature in features:
            title: str = features[feature]["Title"]
            interval: str = f"{self.start_date}..{self.end_date}"
            data[title] = {
                CloudCoverageJson.TITLE: features[feature]["Title"],
                CloudCoverageJson.CLOUD: features[feature]["CloudCover"],
                CloudCoverageJson.DATE: features[feature]["Date"],
                CloudCoverageJson.INTERVAL: interval,
                CloudCoverageJson.TILE: title.split("_")[5],
            }
        self.shared.dumb_to_json(path=path, data=data)
        logger.info("Downloaded data cloud information successfully saved.")
        return path

    @staticmethod
    def _create_image_for_area_covered(search_result: Dict[str, Any], dir_path: str) -> None:
        logger.info("Checking images areas. Creating image...")
        data: List[str] = []
        for index, (key, value) in enumerate(search_result.items()):
            coordinate: Any = value.get("Coordinates")[0]
            polygon_wkt: str = f"POLYGON (({' ,'.join(f'{x} {y}' for x, y in coordinate)}))"
            data.append(polygon_wkt)

        df: DataFrame = DataFrame(data, columns=["geometry"])
        df["geometry"] = df["geometry"].apply(wkt.loads)
        gdf: GeoDataFrame = GeoDataFrame(df, crs="epsg:4326")
        try:
            m: Map = Map(location=[54.90942, 23.91456], zoom_start=7, tiles="CartoDB positron")
            for _, r in gdf.iterrows():
                sim_geo: GeoSeries | str = GeoSeries(r["geometry"]).simplify(tolerance=0.000001)
                geo_j = sim_geo.to_json()
                geo_j: GeoJson = GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
                geo_j.add_to(m)
            img_data = m._to_png(1)
            img: Image = Image.open(BytesIO(img_data))
            img.save(os.path.join(dir_path, os.path.basename(dir_path + ".png")))
            img.show(os.path.join(dir_path, os.path.basename(dir_path + ".png")))
            logger.info("Image saved successfully.")
            if os.path.isfile("geckodriver.log"):
                try:
                    os.remove("geckodriver.log")
                except PermissionError:
                    pass
        except Exception:
            logger.error(
                "Cannot create coverage photo due to server error. If coverage photo is necessary rerunning script should"
                "solve the problem"
            )

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

    def _generate_parameters(self, api) -> Dict[DownloadInfo, Any]:
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
            self._request_analysis(files=features, size=general_size, available_count=online_count)
            if len(features_info) == 0:
                logger.error("No data was found according to the given criteria. Please try again.")
            else:
                download_process = True
        return {
            DownloadInfo.FEATURES: features,
            DownloadInfo.FEATURES_INFO: features_info,
            DownloadInfo.GENERAL_SIZE: general_size,
            DownloadInfo.ONLINE_COUNT: online_count,
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

    @staticmethod
    def _ask_for_interpolation() -> bool:
        while True:
            boolean = str(input("Do you want to apply image interpolation (Y/N)? "))
            if boolean.lower() == YesNo.YES:
                return True
            elif boolean.lower() == YesNo.NO:
                logger.info("Cloud interpolation algorithm is skipped.")
                return False
            else:
                logger.info("Error. Please specify an answer.")
