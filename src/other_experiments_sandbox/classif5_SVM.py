import time
import numpy as np
import pandas as pd
from osgeo import gdal
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, precision_score, recall_score
from sklearn.impute import SimpleImputer

gdal.UseExceptions()
start_time = time.time()

from enum import Enum


class LabelColumn(str, Enum):
    COD = "COD"

    def __str__(self) -> str:
        return self.value


class DataColumns(str, Enum):
    S2_2 = "S2_2"
    S2_3 = "S2_3"
    S2_4 = "S2_4"
    S2_5 = "S2_5"
    S2_6 = "S2_6"
    S2_7 = "S2_7"
    S2_8 = "S2_8"
    S2_8A = "S2_8A"
    S2_11 = "S2_11"
    S2_12 = "S2_12"
    NDTI = "NDTI"
    NDVIre = "NDVIre"
    MNDWI = "MNDWI"

    def __str__(self) -> str:
        return self.value


def createGeotiff(outRaster, dataG, transform, proj):
    driver = gdal.GetDriverByName("GTiff")
    rowsG, colsG = dataG.shape
    rasterDS = driver.Create(outRaster, colsG, rowsG, 1, gdal.GDT_Byte)
    rasterDS.SetGeoTransform(transform)
    rasterDS.SetProjection(proj)
    band = rasterDS.GetRasterBand(1)
    band.WriteArray(dataG)
    rasterDS = None


train_data_path = "/Users/juliusjancevicius/Library/CloudStorage/OneDrive-Personal/VGTU/III Kursas/Intelektualios informacinės sistemos/libraries/training_ground_August.csv"
test_data_path = "/Users/juliusjancevicius/Library/CloudStorage/OneDrive-Personal/VGTU/III Kursas/Intelektualios informacinės sistemos/libraries/validation_ground_August.csv"
# inputRaster = (
#     "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/"
#     "2024-07-09..2024-07-10 0-1%/CLEANED 2024-07-09..2024-07-10 0-1%/2024-07-09..2024-07-10 T35UMA.tiff"
# )
outputRaster = "NEWWW1.tiff"

train_df = pd.read_csv(train_data_path, sep=",")
test_df = pd.read_csv(test_data_path, sep=",")

data_columns = [col for col in DataColumns]
label_column = LabelColumn.COD

imputer = SimpleImputer(strategy="mean")

X_train = imputer.fit_transform(train_df[data_columns].values)
y_train = train_df[label_column].values

X_test = imputer.transform(test_df[data_columns].values)
y_test = test_df[label_column].values

clf = SVC(kernel="rbf", C=1, gamma="scale")
print("Training SVM")
clf.fit(X_train, y_train)

# Predict on the test set
print("Predicting with SVM")
y_pred_test = clf.predict(X_test)

# Calculate and print accuracy
accuracy = accuracy_score(y_test, y_pred_test)
print(f"Accuracy on the test set: {accuracy * 100:.2f}%")

# Calculate precision, recall, F1 score, and Cohen's kappa
precision = precision_score(y_test, y_pred_test, average="weighted", zero_division=1)
recall = recall_score(y_test, y_pred_test, average="weighted")
f1 = f1_score(y_test, y_pred_test, average="weighted")
kappa = cohen_kappa_score(y_test, y_pred_test)

# Print the calculated metrics
print(f"Precision on the test set: {precision * 100:.2f}%")
print(f"Recall on the test set: {recall * 100:.2f}%")
print(f"F1-score on the test set: {f1 * 100:.2f}%")
print(f"Cohen's Kappa on the test set: {kappa:.2f}")

ds = gdal.Open(inputRaster, gdal.GA_ReadOnly)
rows = ds.RasterYSize
cols = ds.RasterXSize
bands = ds.RasterCount
geo_transform = ds.GetGeoTransform()
projection = ds.GetProjectionRef()
array = ds.ReadAsArray().astype("int16")
ds = None

array = np.stack(array, axis=2)
array = np.reshape(array, [rows * cols, bands])
test = pd.DataFrame(array, dtype="int16")
del array

test_imputed = imputer.transform(test)

y_pred = clf.predict(test_imputed)
del test_imputed
classification_SVM = y_pred.reshape((rows, cols))
del y_pred

# Save the classified raster
print("Saving")
createGeotiff(
    outRaster=outputRaster,
    dataG=classification_SVM,
    transform=geo_transform,
    proj=projection,
)
del classification_SVM
end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.2f} seconds")
