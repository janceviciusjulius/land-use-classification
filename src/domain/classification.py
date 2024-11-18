import os.path
import pickle
import re
import sys
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from loguru import logger
from osgeo import gdal
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from additional.logger_configuration import configurate_logger
from domain.shared import Shared
from exceptions.exceptions import MonthExtractionException
from schema.algorithm import Algorithm
from schema.columns import DataColumns, LabelColumn
from schema.constants import Constants
from schema.file_modes import FileMode
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.library_type import LibraryType
from schema.metadata_types import ParametersJson
from schema.months import Month
from schema.regexes import Regex
from schema.root_folders import RootFolders
from schema.yes_no import YesNo

configurate_logger()


class Classification:
    MAX_DEPTH: int = 100
    ESTIMATORS: int = 100
    N_JOBS: int = -1

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder(algorithm=Algorithm.CLASSIFICATION)
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.models: Dict[Month, str] = {}

    def classify(self):
        if self._ask_for_relearning():
            self._train_and_save_model()

        self.models = self._get_model_paths()
        self.shared.create_folder(path=self.folders[FolderType.CLASSIFIED])

        for file in self.files:
            file_name: str = os.path.basename(file)
            file_month: int = self._get_month(file_name=file_name)
            output_path: str = os.path.join(self.folders[FolderType.CLASSIFIED], file_name)

            month_map: Dict[int, Month] = self._month_map()
            month_enum: Month = month_map[file_month]
            model = self._load_model(month=month_enum)

            ds = gdal.Open(file, gdal.GA_ReadOnly)
            rows = ds.RasterYSize
            cols = ds.RasterXSize
            bands = ds.RasterCount
            geo_transform = ds.GetGeoTransform()
            proj = ds.GetProjectionRef()
            array = ds.ReadAsArray().astype("int16")
            ds = None

            array = np.stack(array, axis=2)
            array = np.reshape(array, [rows * cols, bands])

            classification_SVM = model.predict(array)
            classification_SVM = classification_SVM.reshape((rows, cols))

            self._createGeotiff(outRaster=output_path, dataG=classification_SVM, transform=geo_transform, proj=proj)
            # TODO: TBC

    @staticmethod
    def _createGeotiff(outRaster, dataG, transform, proj):
        driver = gdal.GetDriverByName("GTiff")
        rowsG, colsG = dataG.shape
        rasterDS = driver.Create(outRaster, colsG, rowsG, 1, gdal.GDT_Byte)
        rasterDS.SetGeoTransform(transform)
        rasterDS.SetProjection(proj)
        band = rasterDS.GetRasterBand(1)
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

    def _group_libraries(self, all_libraries: List[str]) -> Dict[Month, Dict[LibraryType, str]]:
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
        print(grouped_libraries)
        for month, libraries_info in grouped_libraries.items():
            train_library: str = libraries_info[LibraryType.TRAIN]
            validation_library: str = libraries_info[LibraryType.VALIDATION]
            try:
                train_df: DataFrame = pd.read_csv(train_library)
                test_df: DataFrame = pd.read_csv(validation_library)
            except (FileNotFoundError, UnicodeDecodeError) as error:
                logger.error(f"{error.__class__.__name__} on {train_library} library.")
                logger.info(Constants.LINE)
                continue

            X_train: np.ndarray = train_df[[col for col in DataColumns]].values
            y_train: np.ndarray = train_df[LabelColumn.COD].values
            X_test: np.ndarray = test_df[[col for col in DataColumns]].values
            y_test: np.ndarray = test_df[LabelColumn.COD].values

            filename: str = self.shared.file_from_path(path=train_library)
            filename_without_ext: str = self.shared.remove_ext(file=filename)
            model_filename = self.shared.add_file_ext(file_name=filename_without_ext, ext=FileType.PKL)
            model_path: str = os.path.join(self.shared.root_folders[RootFolders.MODEL_FOLDER], model_filename)

            clf = RandomForestClassifier(
                n_estimators=self.ESTIMATORS,
                n_jobs=self.N_JOBS,
                max_depth=self.MAX_DEPTH,
            )
            clf.fit(X_train, y_train)
            y_pred_test = clf.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred_test)
            precision = precision_score(y_test, y_pred_test, average="weighted")
            recall = recall_score(y_test, y_pred_test, average="weighted")
            f1 = f1_score(y_test, y_pred_test, average="weighted")
            kappa = cohen_kappa_score(y_test, y_pred_test)

            accuracy_result: str = f"Accuracy on the test set: {accuracy * 100:.2f}%"
            logger.info(accuracy_result)
            precision_result: str = f"Precision on the test set: {precision * 100:.2f}%"
            logger.info(precision_result)
            recall_result: str = f"Recall on the test set: {recall * 100:.2f}%"
            logger.info(recall_result)
            f1_result: str = f"F1-score on the test set: {f1 * 100:.2f}%"
            logger.info(f1_result)
            kappa_result: str = f"Cohen's Kappa on the test set: {kappa * 100:.2f}"
            logger.info(kappa_result)

            path_info: str = f"Model saved to: {model_path}"
            messages: List[str] = [
                month.value.upper(),
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
        file_path: str = os.path.join(self.shared.root_folders[RootFolders.PROGRAM_FOLDER], Constants.ACCURACIES_FILE)
        with open(file_path, FileMode.APPEND) as file:
            for message in messages:
                file.write(message + Constants.NEW_LINE)

    def _initialize_file(self) -> None:
        file_path: str = os.path.join(self.shared.root_folders[RootFolders.PROGRAM_FOLDER], Constants.ACCURACIES_FILE)
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
        match = re.search(Regex.DATE_REGEX, file_name)
        if match:
            file_month = match.group(2)
            return int(file_month)
        else:
            raise MonthExtractionException(f"Cannot extract month from {file_name}")
