from typing import List, Any, Dict

from osgeo import gdal
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, cohen_kappa_score
from sklearn.model_selection import train_test_split

from domain.shared import Shared
from schema.folder_types import FolderType
from schema.metadata_types import ParametersJson


class Classification:
    MAX_DEPTH: int = 100
    ESTIMATORS: int = 100
    N_JOBS: int = -1
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.3

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder()
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]

    def classify(self):
        pass

    @staticmethod
    def _createGeotiff(out_raster, data_g, transform, proj) -> str:
        driver = gdal.GetDriverByName("GTiff")
        rowsG, colsG = data_g.shape
        rasterDS = driver.Create(out_raster, colsG, rowsG, 1, gdal.GDT_Byte)
        rasterDS.SetGeoTransform(transform)
        rasterDS.SetProjection(proj)
        band = rasterDS.GetRasterBand(1)
        band.WriteArray(data_g)
        rasterDS = None
        return out_raster

    def _train_and_save_model(self, training_data, labels, model_path):
        training_libraries: List[str] =
        for library in training_libraries:


        X_train, X_test, y_train, y_test = train_test_split(
            training_data, labels, test_size=self.TEST_SIZE, random_state=self.RANDOM_STATE
        )

        clf: RandomForestClassifier = RandomForestClassifier(
            n_estimators=self.ESTIMATORS, n_jobs=self.N_JOBS, max_depth=self.MAX_DEPTH
        )
        logger.info("Training the model...")
        clf.fit(X_train, y_train)

        y_pred_test = clf.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test, average="weighted")
        recall = recall_score(y_test, y_pred_test, average="weighted")
        f1 = f1_score(y_test, y_pred_test, average="weighted")
        kappa = cohen_kappa_score(y_test, y_pred_test)

        # Print the calculated metrics
        print(f"Accuracy on the test set: {accuracy * 100:.2f}%")
        print(f"Precision on the test set: {precision * 100:.2f}%")
        print(f"Recall on the test set: {recall * 100:.2f}%")
        print(f"F1-score on the test set: {f1 * 100:.2f}%")
        print(f"Cohen's Kappa on the test set: {kappa:.2f}")

        # Save the trained model
        joblib.dump(clf, model_path)
        print(f"Model saved to {model_path}")
