import os.path
import pickle
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from loguru import logger
from osgeo import gdal
from osgeo.gdal import Dataset, Driver
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, precision_score, recall_score

# from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from additional.logger_configuration import configurate_logger
from domain.shared import Shared
from exceptions.exceptions import MonthExtractionException
from schema.accuracy_metrics import AccuracyMetrics
from schema.algorithm import Algorithm
from schema.columns import DataColumns, LabelColumn
from schema.constants import Constants
from schema.file_modes import FileMode
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.formats import Format
from schema.library_type import LibraryType
from schema.metadata_types import ParametersJson
from schema.months import Month
from schema.reading_types import ReadingType
from schema.regexes import Regex
from schema.root_folders import RootFolders
from schema.unit_type import UnitType
from schema.yes_no import YesNo

configurate_logger()


class Classification:
    MAX_DEPTH: int = 10
    ESTIMATORS: int = 10
    N_JOBS: int = -1
    NO_DATA_VALUE: int = 0

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder(algorithm=Algorithm.CLASSIFICATION)
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.models: Dict[Month, str] = {}

    def classify(self) -> None:
        if self._ask_for_relearning():
            self._train_and_save_model()

        self.models = self._get_model_paths()
        self.shared.create_folder(path=self.folders[FolderType.CLASSIFIED])
        self.shared.create_folder(path=self.folders[FolderType.CONFIDENCE])

        pbar: tqdm = tqdm(self.files, unit=UnitType.FILE)
        for index, file in enumerate(pbar):
            pbar.set_description(f"Classifying {index+1} image")
            file_name: str = os.path.basename(str(file))
            file_month: int = self._get_month(file_name=file_name)
            output_path: str = os.path.join(self.folders[FolderType.CLASSIFIED], file_name)

            confidence_file_name: str = f"Confidence {file_name}"
            conf_output_path: str = os.path.join(self.folders[FolderType.CONFIDENCE], confidence_file_name)

            month_map: Dict[int, Month] = self._month_map()
            month_enum: Month = month_map[file_month]
            model = self._load_model(month=month_enum)

            ds: Any = gdal.Open(file, gdal.GA_ReadOnly)
            rows: int = ds.RasterYSize
            cols: int = ds.RasterXSize
            bands: int = ds.RasterCount
            geo_trans: Any = ds.GetGeoTransform()
            proj: Any = ds.GetProjectionRef()
            array: np.array = ds.ReadAsArray().astype(ReadingType.INT16)
            ds: None = None

            array: np.array = np.stack(array, axis=2)
            array: np.array = np.reshape(array, [rows * cols, bands])

            # scaler = StandardScaler()
            # array = scaler.fit_transform(array)

            class_result: np.array = model.predict(array)
            probabilities: np.array = model.predict_proba(array)
            confidence: np.array = np.max(probabilities, axis=1)

            class_result: np.array = class_result.reshape((rows, cols))
            confidence: np.array = confidence.reshape((rows, cols))

            class_result: np.array = self._remove_clouds(input_file=str(file), class_result=class_result)
            confidence: np.array = self._remove_clouds(input_file=str(file), class_result=confidence)
            confidence: np.array = np.round(confidence, decimals=2)

            self._createGeotiff(outRaster=output_path, dataG=class_result, transform=geo_trans, proj=proj)
            self._createGeotiff(
                outRaster=conf_output_path, dataG=confidence, transform=geo_trans, proj=proj, data_type=gdal.GDT_Float32
            )
        logger.warning("End of classification process.")
        return None

    @staticmethod
    def _remove_clouds(input_file: str, class_result: np.array) -> np.array:
        test_raster: Any = gdal.Open(input_file, gdal.GA_ReadOnly)
        band_1: Any = test_raster.GetRasterBand(1)
        band_1_array: np.array = band_1.ReadAsArray().astype(ReadingType.INT16)
        class_result[band_1_array == 0] = 0
        return class_result

    def _createGeotiff(
        self,
        outRaster: str,
        dataG: np.array,
        transform: Any,
        proj: Any,
        data_type: int = gdal.GDT_Byte,
    ):
        driver: Driver = gdal.GetDriverByName(Format.GTIFF)
        rowsG, colsG = dataG.shape
        rasterDS: Optional[Dataset] = driver.Create(outRaster, colsG, rowsG, 1, data_type)
        rasterDS.SetGeoTransform(transform)
        rasterDS.SetProjection(proj)
        band: Any = rasterDS.GetRasterBand(1)
        band.SetNoDataValue(self.NO_DATA_VALUE)
        band.WriteArray(dataG)
        rasterDS = None

    def _get_model_paths(self) -> Dict[Month, str]:
        model_paths: Dict[Month, str] = {}
        model_folder = self.shared.root_folders[RootFolders.MODEL_FOLDER]

        for model_name in os.listdir(model_folder):
            model_path: str = os.path.join(model_folder, model_name)
            for month in Month:
                if month.value in model_name.lower():
                    model_paths[month] = model_path
                    break
        return model_paths

    def _ask_for_relearning(self) -> bool:
        while True:
            boolean: str = str(input("Do you want to relearn classification models (Y/N)? "))
            if boolean.lower() == YesNo.YES:
                return True
            elif boolean.lower() == YesNo.NO:
                return False
            self.shared.clear_console()

    @staticmethod
    def _group_libraries(
        all_libraries: List[str],
    ) -> Dict[Month, Dict[LibraryType, str]]:
        group_libraries: Dict[Month, Dict[LibraryType, str]] = {month: {} for month in Month}
        for library in all_libraries:
            library_name: str = os.path.basename(library)
            for month in Month:
                if str(month) in library_name.lower():
                    for library_type in LibraryType:
                        if str(library_type) in library_name.lower():
                            group_libraries[month][library_type] = library
        return {key: value for key, value in group_libraries.items() if value and len(value) == 2}

    def _train_and_save_model(self) -> None:
        self._initialize_file()
        all_libraries: List[str] = self.shared.list_dir(dir_=self.shared.root_folders[RootFolders.LEARNING_FOLDER])

        grouped_libraries: Dict[Month, Dict[LibraryType, str]] = self._group_libraries(all_libraries=all_libraries)
        for month, libraries_info in grouped_libraries.items():
            logger.info(f"Training {month}...")
            train_library: str = libraries_info[LibraryType.TRAIN]
            validation_library: str = libraries_info[LibraryType.VALIDATION]
            try:
                train_df: DataFrame = pd.read_csv(train_library)
                test_df: DataFrame = pd.read_csv(validation_library)

                train_df = train_df.dropna()
                test_df = test_df.dropna()
            except (FileNotFoundError, UnicodeDecodeError) as error:
                logger.error(f"{error.__class__.__name__} on {train_library} library.")
                logger.info(Constants.LINE)
                continue

            X_train: np.ndarray = train_df[[col for col in DataColumns]].values
            y_train: np.ndarray = train_df[LabelColumn.COD].values
            X_test: np.ndarray = test_df[[col for col in DataColumns]].values
            y_test: np.ndarray = test_df[LabelColumn.COD].values

            # #
            # scaler = StandardScaler()
            # X_train = scaler.fit_transform(X_train)
            # X_test = scaler.transform(X_test)
            # #

            filename: str = self.shared.file_from_path(path=train_library)
            filename_without_ext: str = self.shared.remove_ext(file=filename)
            model_filename = self.shared.add_file_ext(file_name=filename_without_ext, ext=FileType.PKL)
            model_path: str = os.path.join(self.shared.root_folders[RootFolders.MODEL_FOLDER], model_filename)

            clf = RandomForestClassifier(n_estimators=self.ESTIMATORS, n_jobs=self.N_JOBS, max_depth=self.MAX_DEPTH)
            clf.fit(X_train, y_train)
            y_pred_test: np.array = clf.predict(X_test)

            accuracy: float | int = accuracy_score(y_test, y_pred_test)
            precision: float | int = precision_score(
                y_test, y_pred_test, average=AccuracyMetrics.ACCURACY_WEIGHTED, zero_division=0
            )
            recall: float | int = recall_score(
                y_test, y_pred_test, average=AccuracyMetrics.ACCURACY_WEIGHTED, zero_division=0
            )
            f1: float | int = f1_score(y_test, y_pred_test, average=AccuracyMetrics.ACCURACY_WEIGHTED, zero_division=0)
            kappa: float | int = cohen_kappa_score(y_test, y_pred_test)

            general_info: str = f"{month.value.upper()} with MAX_DEPTH: {self.MAX_DEPTH} ESTIMATORS: {self.ESTIMATORS}"
            logger.info(general_info)

            accuracy_result: str = f"Accuracy on the test set: {accuracy * 100:.2f}%"
            logger.info(accuracy_result)
            precision_result: str = f"Precision on the test set: {precision * 100:.2f}%"
            logger.info(precision_result)
            recall_result: str = f"Recall on the test set: {recall * 100:.2f}%"
            logger.info(recall_result)
            f1_result: str = f"F1-score on the test set: {f1 * 100:.2f}%"
            logger.info(f1_result)
            kappa_result: str = f"Cohen's Kappa on the test set: {kappa * 100:.2f}%"
            logger.info(kappa_result)

            path_info: str = f"Model saved to: {model_path}"
            messages: List[str] = [
                general_info,
                accuracy_result,
                precision_result,
                recall_result,
                f1_result,
                kappa_result,
                path_info,
                Constants.LINE,
            ]
            self._write_accuracies_to_file(messages=messages)

            with open(model_path, FileMode.WRITE_B) as model_file:
                pickle.dump(clf, model_file)

            logger.info(path_info)
            logger.info(Constants.LINE)

    def _write_accuracies_to_file(self, messages: List[str]) -> None:
        file_path: str = os.path.join(
            self.shared.root_folders[RootFolders.PROGRAM_FOLDER],
            Constants.ACCURACIES_FILE,
        )
        with open(file_path, FileMode.APPEND) as file:
            for message in messages:
                file.write(message + Constants.NEW_LINE)

    def _initialize_file(self) -> None:
        file_path: str = os.path.join(
            self.shared.root_folders[RootFolders.PROGRAM_FOLDER],
            Constants.ACCURACIES_FILE,
        )
        with open(file_path, FileMode.WRITE):
            pass

    def _load_model(self, month: Month):
        try:
            with open(self.models[month], FileMode.READ_B) as file:
                return pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError) as error:
            logger.error(f"{error.__class__.__name__} on {str(month)} model.")

    @staticmethod
    def _month_map() -> Dict[int, Month]:
        return {i: month_enum for i, month_enum in enumerate(Month, start=1)}

    @staticmethod
    def _get_month(file_name: str) -> int:
        for regex in Regex:
            match = re.search(regex, file_name)
            if match:
                return int(match.group(2))
        raise MonthExtractionException(f"Cannot extract month from {file_name}")
