import os
import time
from tkinter.filedialog import askopenfilename
from tkinter import *
import datetime as dt
from osgeo import ogr
import sys

def choose_shp_file():
    # Window where .shp or .gpkg file is chosen
    root = Tk()
    root.title('File Open Dialog')
    root.resizable(False, False)
    root.geometry('300x150')
    filetypes = (('ESRI Shapefile', '*.shp'), ('GeoPackage', '*.gpkg'),)
    shp_filename = askopenfilename(
        title='Open a file',
        filetypes=filetypes)
    root.destroy()
    return shp_filename


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)


def process_input_file(input_file):
    # Checking and validating features in file (SHP01)
    print("Starting file corrections")
    shape_file = ogr.Open(input_file, 1)  # 1 = update mode
    layer = shape_file.GetLayer()
    try:
        for feature in layer:
            geom = feature.GetGeometryRef()
            if not geom.IsValid():
                feature.SetGeometry(geom.MakeValid())
                layer.SetFeature(feature)
                assert feature.GetGeometryRef().IsValid()
        layer.ResetReading()
        assert all(feature.GetGeometryRef().IsValid() for feature in layer)
    except AttributeError:
        print("Cannot fix file. File do not have GeometryRef information")
        sys.exit(1)
    print("End of file correction")


if __name__ == "__main__":
    start_time = time.time()
    clear_console()
    input_shape = choose_shp_file()
    print(input_shape)
    process_input_file(input_file=input_shape)
    conversion = dt.timedelta(seconds=round(time.time() - start_time))
    print(f"Request completed successfully. Operating time: {str(conversion)}.")
