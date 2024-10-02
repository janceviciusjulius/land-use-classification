import time

import numpy as np
import pandas as pd
from osgeo import gdal
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

gdal.UseExceptions()
start_time = time.time()
ESTIMATORS = 100


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


inputRaster = (
    "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/"
    "2024-07-09..2024-07-10 0-1%/CLEANED 2024-07-09..2024-07-10 0-1%/2024-07-09..2024-07-10 T35UMA.tiff"
)
df = pd.read_csv(
    "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/"
    "learning_data/training_ground_July copy.csv",
    sep=",",
)
outputRaster = "NEW1.tiff"

data_columns = [col for col in DataColumns]
label_column = LabelColumn.COD

print(data_columns)
print(label_column)

data = df[data_columns]
label = df[label_column]
label_values = df["COD"].unique()
print(label_values)
del df

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data.values, label.values, test_size=0.3, random_state=42)

# Train the model
clf = RandomForestClassifier(n_estimators=ESTIMATORS, n_jobs=-1, max_depth=100)
print("Training")
clf.fit(X_train, y_train)

# Predict on the test set
print("Predicting")
y_pred_test = clf.predict(X_test)

# Calculate and print accuracy
accuracy = accuracy_score(y_test, y_pred_test)
print(f"Accuracy on the test set: {accuracy * 100:.2f}%")

# Calculate precision, recall, F1 score, and Cohen's kappa
precision = precision_score(y_test, y_pred_test, average="weighted")
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

# Predict on the full raster data
y_pred = clf.predict(test)
del test
classification_RF = y_pred.reshape((rows, cols))
del y_pred

# Save the classified raster
print("Saving")
createGeotiff(
    outRaster=outputRaster,
    dataG=classification_RF,
    transform=geo_transform,
    proj=projection,
)
del classification_RF
end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.2f} seconds")
