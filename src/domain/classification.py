import os.path
import pickle
from typing import List, Any, Dict, BinaryIO

import numpy as np
import pandas as pd
from osgeo import gdal
from loguru import logger
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, cohen_kappa_score
from sklearn.model_selection import train_test_split

from domain.shared import Shared
from schema.columns import DataColumns, LabelColumn
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.metadata_types import ParametersJson
from schema.root_folders import RootFolders


class Classification:
    MAX_DEPTH: int = 100
    ESTIMATORS: int = 100
    N_JOBS: int = -1
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder()
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]

    def classify(self):
        self._train_and_save_model()

    def _train_and_save_model(self):
        train_libraries: List[str] = self.shared.list_dir(dir_=self.shared.root_folders[RootFolders.LEARNING_FOLDER])
        for train_library in train_libraries:
            try:
                df: DataFrame = pd.read_csv(train_library)
            except UnicodeDecodeError:
                logger.error(f"{train_library}")
                continue

            data: np.ndarray = df[[col for col in DataColumns]].values
            labels: np.ndarray = df[LabelColumn.COD].values

            filename: str = self.shared.file_from_path(path=train_library)
            filename_without_ext = self.shared.remove_ext(file=filename)
            model_filename = self.shared.add_file_ext(file_name=filename_without_ext, ext=FileType.PKL)
            model_path: str = os.path.join(self.shared.root_folders[RootFolders.TRAINING_FOLDER], model_filename)

            X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=self.TEST_SIZE,
                                                                random_state=self.RANDOM_STATE)

            clf = RandomForestClassifier(n_estimators=self.ESTIMATORS, n_jobs=self.N_JOBS, max_depth=self.MAX_DEPTH)
            clf.fit(X_train, y_train)
            y_pred_test = clf.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred_test)
            precision = precision_score(y_test, y_pred_test, average="weighted")
            recall = recall_score(y_test, y_pred_test, average="weighted")
            f1 = f1_score(y_test, y_pred_test, average="weighted")
            kappa = cohen_kappa_score(y_test, y_pred_test)

            print(f"Accuracy on the test set: {accuracy * 100:.2f}%")
            print(f"Precision on the test set: {precision * 100:.2f}%")
            print(f"Recall on the test set: {recall * 100:.2f}%")
            print(f"F1-score on the test set: {f1 * 100:.2f}%")
            print(f"Cohen's Kappa on the test set: {kappa:.2f}")

            with open(model_path, 'wb') as model_file:
                pickle.dump(clf, model_file)
            print(f"Model saved to {model_path}")