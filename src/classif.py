import numpy as np
import pandas as pd
from osgeo import gdal
from sklearn.ensemble import RandomForestClassifier

ESTIMATORS = 100


def createGeotiff(outRaster, dataG, transform, proj):
    driver = gdal.GetDriverByName("GTiff")
    rowsG, colsG = dataG.shape
    rasterDS = driver.Create(outRaster, colsG, rowsG, 1, gdal.GDT_Byte)
    rasterDS.SetGeoTransform(transform)
    rasterDS.SetProjection(proj)
    band = rasterDS.GetRasterBand(1)
    band.WriteArray(dataG)
    rasterDS = None


inputRaster = "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-07-09..2024-07-10 0-1%/CLEANED 2024-07-09..2024-07-10 0-1%/2024-07-09..2024-07-10 T35UMA.tiff"
df = pd.read_csv(
    "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/learning_data/training_ground_June.csv",
    sep=",",
)
outputRaster = "demo.tiff"
data = df[
    ["S2_2", "S2_3", "S2_4", "S2_5", "S2_6", "S2_7", "S2_8", "S2_8A", "S2_11", "S2_12", "NDTI", "NDVIre", "MNDWI"]
]
label = df["COD"]
del df
ds = gdal.Open(inputRaster, gdal.GA_ReadOnly)
rows = ds.RasterYSize
cols = ds.RasterXSize
bands = ds.RasterCount
geo_transform = ds.GetGeoTransform()
projection = ds.GetProjectionRef()
array = ds.ReadAsArray().astype("uint16")
ds = None
array = np.stack(array, axis=2)
array = np.reshape(array, [rows * cols, bands])
test = pd.DataFrame(array, dtype="uint16")
del array
clf = RandomForestClassifier(n_estimators=ESTIMATORS)
print("Training")
clf.fit(data.values, label.values)
del data, label
print("Predicting")
y_pred = clf.predict(test)
del test
classification_RF = y_pred.reshape((rows, cols))
del y_pred
print("Saving")
createGeotiff(
    outRaster=outputRaster,
    dataG=classification_RF,
    transform=geo_transform,
    proj=projection,
)
del classification_RF
