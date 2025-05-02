import os
import re
import shutil
import sys
from typing import Any, Dict, List

import numpy as np
from bs4 import BeautifulSoup
from loguru import logger
from osgeo import gdal

from additional.logger_configuration import configurate_logger
from domain.shared import Shared
from schema.algorithm import Algorithm
from schema.folder_types import FolderType
from schema.metadata_types import ParametersJson
from schema.read_type import ReadType

configurate_logger()


class PostProcessing:
    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder(algorithm=Algorithm.POST_PROCESSING)
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.conf_files: Dict[str, str] = {}

    def find_confidence_maps(self):
        for file in self.files:
            file_name = os.path.basename(file)
            for conf_file in os.listdir(self.folders[FolderType.CONFIDENCE]):
                if file_name in conf_file:
                    conf_file_path = os.path.join(self.folders[FolderType.CONFIDENCE], conf_file)
                    self.conf_files[file] = conf_file_path

    def create_raster_copies(self):
        post_folder = self.folders[FolderType.POST_PROCESSED]
        for file in self.files:
            dest = os.path.join(post_folder, os.path.basename(file))
            try:
                shutil.copy(src=file, dst=dest)
            except PermissionError:
                logger.error(f"File {file} is opened with another program. Skipping file.")
                continue
        self.files = [os.path.join(post_folder, file) for file in os.listdir(post_folder)]

    @staticmethod
    def _get_month(file_name: str):
        m = re.search(r"(\d{4})(\d{2})(\d{2})", file_name)
        return int(m.group(2))

    def post_process(self):
        self.shared.create_folder(path=self.folders[FolderType.POST_PROCESSED])
        self.create_raster_copies()
        self.find_confidence_maps()

        for index, file in enumerate(self.files):
            month_ = self._get_month(file_name=os.path.basename(file))

            raster_ = gdal.Open(file, 1)
            raster_array = raster_.ReadAsArray().astype(ReadType.UINT8)
            conf_raster = self.conf_files[file]
            conf_raster = gdal.Open(conf_raster, 1)
            conf_raster_array = conf_raster.ReadAsArray().astype(ReadType.FLOAT32)

            mask = self.clauses(conf_arr=conf_raster_array, raster_arr=raster_array, month=month_)
            raster_array[mask == False] = 99
            raster_.WriteArray(raster_array)

            raster_, raster_array = None, None
            conf_raster, conf_raster_array, mask = None, None, None
            logger.info(f"Processed {index+1} file")
        logger.info("End of Post Processing step")

    @staticmethod
    def clauses(conf_arr, raster_arr, month):
        mask = np.logical_or.reduce(
            (
                np.logical_and(
                    np.logical_and(conf_arr >= 0, month in [4, 5, 6, 7, 8, 9, 10, 1]),
                    raster_arr == 0,
                ),
                # April
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 4), raster_arr == 11),
                np.logical_and(np.logical_and(conf_arr > 0.36, month == 4), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 4), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 4), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.43, month == 4), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.54, month == 4), raster_arr == 61),
                # May
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 5), raster_arr == 11),
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 5), raster_arr == 14),
                np.logical_and(np.logical_and(conf_arr > 0.37, month == 5), raster_arr == 16),
                np.logical_and(np.logical_and(conf_arr > 0.36, month == 5), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 5), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 5), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.43, month == 5), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.54, month == 5), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 5), raster_arr == 62),
                # June
                np.logical_and(np.logical_and(conf_arr > 0.41, month == 6), raster_arr == 12),
                np.logical_and(np.logical_and(conf_arr > 0.49, month == 6), raster_arr == 16),
                np.logical_and(np.logical_and(conf_arr > 0.29, month == 6), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.39, month == 6), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 6), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.58, month == 6), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.48, month == 6), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.39, month == 6), raster_arr == 62),
                # July
                np.logical_and(np.logical_and(conf_arr > 0.41, month == 7), raster_arr == 12),
                np.logical_and(np.logical_and(conf_arr > 0.4, month == 7), raster_arr == 16),
                np.logical_and(np.logical_and(conf_arr > 0.29, month == 7), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.39, month == 7), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 7), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.78, month == 7), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.48, month == 7), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.39, month == 7), raster_arr == 62),
                # August
                np.logical_and(np.logical_and(conf_arr > 0.26, month == 8), raster_arr == 11),
                np.logical_and(np.logical_and(conf_arr > 0.47, month == 8), raster_arr == 13),
                np.logical_and(np.logical_and(conf_arr > 0.55, month == 8), raster_arr == 16),
                np.logical_and(np.logical_and(conf_arr > 0.45, month == 8), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.31, month == 8), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 8), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.39, month == 8), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 8), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.53, month == 8), raster_arr == 62),
                # September
                np.logical_and(np.logical_and(conf_arr > 0.38, month == 9), raster_arr == 11),
                np.logical_and(np.logical_and(conf_arr > 0.46, month == 9), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.46, month == 9), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 9), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.63, month == 9), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 9), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.53, month == 9), raster_arr == 62),
                # October
                np.logical_and(np.logical_and(conf_arr > 0.32, month == 10), raster_arr == 11),
                np.logical_and(np.logical_and(conf_arr > 0.46, month == 10), raster_arr == 15),
                np.logical_and(np.logical_and(conf_arr > 0.55, month == 10), raster_arr == 21),
                np.logical_and(np.logical_and(conf_arr > 0.4, month == 10), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.25, month == 10), raster_arr == 41),
                np.logical_and(np.logical_and(conf_arr > 0.68, month == 10), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 10), raster_arr == 61),
                np.logical_and(np.logical_and(conf_arr > 0.3, month == 10), raster_arr == 62),
                # Forest
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 31),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 32),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 33),
                # Urban
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 51),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 52),
                np.logical_and(np.logical_and(conf_arr > 0.5, month == 1), raster_arr == 53),
            )
        )
        return mask
