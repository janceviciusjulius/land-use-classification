import numpy as np
from osgeo import gdal

def clauses(conf_arr, raster_arr, month):
    # add = 0.05
    mask = np.logical_or.reduce(
        (
            np.logical_and(
                np.logical_and(conf_arr > 0.01, month in [4, 5, 6, 7, 8, 9, 10, 1]),
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
            np.logical_and(np.logical_and(conf_arr > (0.26 - 0.06), month == 8), raster_arr == 11),
            np.logical_and(np.logical_and(conf_arr > (0.47 - 0.06), month == 8), raster_arr == 13),
            np.logical_and(np.logical_and(conf_arr > (0.55 - 0.06), month == 8), raster_arr == 16),
            np.logical_and(np.logical_and(conf_arr > (0.45 - 0.06), month == 8), raster_arr == 21),
            np.logical_and(np.logical_and(conf_arr > (0.31 - 0.06), month == 8), raster_arr == 31),
            np.logical_and(np.logical_and(conf_arr > (0.25 - 0.06), month == 8), raster_arr == 41),
            np.logical_and(np.logical_and(conf_arr > (0.39 - 0.06), month == 8), raster_arr == 51),
            np.logical_and(np.logical_and(conf_arr > (0.25 - 0.06), month == 8), raster_arr == 61),
            np.logical_and(np.logical_and(conf_arr > (0.53 - 0.06), month == 8), raster_arr == 62),
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



conf_raster = gdal.Open('/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-08-01..'
                        '2024-09-01 0-5%/CONFIDENCE 2024-08-01..2024-09-01 0-5%/Confidence 4. 20240828 T35ULA 0.18% copy.tiff', 1)
conf_raster_array = conf_raster.ReadAsArray().astype("float32")

raster_ = gdal.Open('/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/SU AUSRINE/CLASS copy.tif', 1)
raster_array = raster_.ReadAsArray().astype("uint8")

mask = clauses(conf_arr=conf_raster_array, raster_arr=raster_array, month=8)
raster_array[mask == False] = 99
raster_.WriteArray(raster_array)
raster_, raster_array = None, None
conf_raster, conf_raster_array, mask = None, None, None