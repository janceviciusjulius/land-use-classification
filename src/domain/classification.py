import os.path
import pickle
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
from schema.algorithm import Algorithm
from schema.columns import DataColumns, LabelColumn
from schema.constants import Constants
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.metadata_types import ParametersJson
from schema.months import Month
from schema.root_folders import RootFolders
from schema.yes_no import YesNo

configurate_logger()


class Classification:
    MAX_DEPTH: int = 100
    ESTIMATORS: int = 100
    N_JOBS: int = -1
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2

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
            print(file)


    def _get_model_paths(self) -> Dict[Month, str]:
        model_paths: Dict[Month, str] = {}
        model_folder = self.shared.root_folders[RootFolders.MODEL_FOLDER]

        for model_name in os.listdir(model_folder):
            model_path = os.path.join(model_folder, model_name)
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
            else:
                self.shared.clear_console()

    def _train_and_save_model(self) -> None:
        self._initialize_file()
        train_libraries: List[str] = self.shared.list_dir(dir_=self.shared.root_folders[RootFolders.LEARNING_FOLDER])
        for train_library in train_libraries:
            try:
                df: DataFrame = pd.read_csv(train_library)
            except UnicodeDecodeError:
                logger.error(f"UnicodeDecodeError on {train_library} library.")
                logger.info(Constants.LINE)
                continue

            data: np.ndarray = df[[col for col in DataColumns]].values
            labels: np.ndarray = df[LabelColumn.COD].values

            filename: str = self.shared.file_from_path(path=train_library)
            filename_without_ext: str = self.shared.remove_ext(file=filename)
            model_filename = self.shared.add_file_ext(file_name=filename_without_ext, ext=FileType.PKL)
            model_path: str = os.path.join(self.shared.root_folders[RootFolders.MODEL_FOLDER], model_filename)

            X_train, X_test, y_train, y_test = train_test_split(
                data, labels, test_size=self.TEST_SIZE, random_state=self.RANDOM_STATE
            )

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

            messages: List[str] = [
                filename_without_ext.upper(),
                accuracy_result,
                precision_result,
                recall_result,
                f1_result,
                kappa_result,
                Constants.LINE,
            ]
            self._write_accuracies_to_file(messages=messages)

            with open(model_path, "wb") as model_file:
                pickle.dump(clf, model_file)
            logger.info(f"Model saved to {model_path}")
            logger.info(Constants.LINE)

    def _write_accuracies_to_file(self, messages: List[str]) -> None:
        file_path: str = os.path.join(self.shared.root_folders[RootFolders.PROGRAM_FOLDER], Constants.ACCURACIES_FILE)
        with open(file_path, "a") as file:
            for message in messages:
                file.write(message + Constants.NEW_LINE)

    def _initialize_file(self) -> None:
        file_path: str = os.path.join(self.shared.root_folders[RootFolders.PROGRAM_FOLDER], Constants.ACCURACIES_FILE)
        with open(file_path, "w"):
            pass

    def load_model(self):
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
