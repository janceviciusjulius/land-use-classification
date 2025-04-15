import time
import numpy as np
import pandas as pd
from osgeo import gdal
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, precision_score, recall_score
from sklearn.impute import SimpleImputer

gdal.UseExceptions()
start_time = time.time()
N_NEIGHBORS = 5  # Number of neighbors for KNN

from enum import Enum


# Enum for the label column
class LabelColumn(str, Enum):
    COD = "COD"

    def __str__(self) -> str:
        return self.value


# Enum for the data columns
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


# File paths
train_data_path = ""
test_data_path = ""
inputRaster = ""
outputRaster = "NEWWW1.tiff"

# Load training data
train_df = pd.read_csv(train_data_path, sep=",")
# Load testing data
test_df = pd.read_csv(test_data_path, sep=",")

# Use Enum for data columns and labels
data_columns = [col for col in DataColumns]
label_column = LabelColumn.COD

# Define the imputer to replace missing values with the mean of the column
imputer = SimpleImputer(strategy="mean")

# Impute missing values in the training dataset
X_train = imputer.fit_transform(train_df[data_columns].values)
y_train = train_df[label_column].values

# Impute missing values in the testing dataset
X_test = imputer.transform(test_df[data_columns].values)
y_test = test_df[label_column].values

# Train the model
clf = KNeighborsClassifier(n_neighbors=N_NEIGHBORS, n_jobs=-1)
print("Training KNN")
clf.fit(X_train, y_train)

# Predict on the test set
print("Predicting with KNN")
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

# Continue with the full prediction process on the raster data
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

# Impute missing values for the full raster data before prediction
test_imputed = imputer.transform(test)

# Predict on the full raster data
y_pred = clf.predict(test_imputed)
del test_imputed
classification_KNN = y_pred.reshape((rows, cols))
del y_pred

# Save the classified raster
print("Saving")
createGeotiff(
    outRaster=outputRaster,
    dataG=classification_KNN,
    transform=geo_transform,
    proj=projection,
)
del classification_KNN
end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.2f} seconds")
