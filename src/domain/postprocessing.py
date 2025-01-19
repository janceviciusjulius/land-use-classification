import os
import shutil
import sys
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

import numpy as np
import options
from bs4 import BeautifulSoup
from osgeo import gdal


def ask_for_files():
    # Window where data files are chosen
    Tk().withdraw()
    input_rasters = askopenfilenames(initialdir=options.return_path())
    input_rasters = list(input_rasters)
    dir_name = os.path.dirname(input_rasters[0])
    if not input_rasters:
        print("No classification result file/files selected.")
        sys.exit(1)
    for raster in input_rasters:
        if "Classified" not in raster or "Categorized" in raster:
            print("Please choose a file with classification water results.")
            sys.exit(1)
    return input_rasters, dir_name


def create_folder_for_results(working_dir):
    post_folder = os.path.join(
        os.path.dirname(working_dir),
        os.path.basename(working_dir.replace("Classified", "PostProcessed")),
    )
    if not os.path.exists(post_folder):
        os.mkdir(post_folder)
    else:
        print("Same data folder exists.", end="\n")
        while True:
            boolean = str(input("Do you want to delete the data (Y/N)? "))
            if boolean.lower() == "y":
                try:
                    shutil.rmtree(post_folder)
                except PermissionError:
                    print("File from this folder is opened with another program.")
                    sys.exit(1)
                print("Data deletion successful\n")
                time.sleep(1)
                os.mkdir(post_folder)
                break
            elif boolean.lower() == "n":
                print("The data is left on disk.\n")
                sys.exit(1)
            else:
                print("\nError. Please specify an answer.")
    return post_folder


def create_raster_copies(selected_files, result_dir):
    try:
        for file in selected_files:
            destination = os.path.join(result_dir, os.path.basename(file))
            shutil.copy(file, destination)
    except PermissionError:
        print("File from this folder is opened with another program.")
        sys.exit(1)
    files = [os.path.join(result_dir, file) for file in os.listdir(result_dir)]
    return files


def get_month(filename):
    if "ground" in filename.lower():
        if "october" in filename.lower():
            return 10
        if "september" in filename.lower():
            return 9
        if "august" in filename.lower():
            return 8
        if "july" in filename.lower():
            return 7
        if "june" in filename.lower():
            return 6
        if "may" in filename.lower():
            return 5
        if "april" in filename.lower():
            return 4
    else:
        return 1


def post_processing(raster_list, classification_dir, result_dir):
    raster_names_list = [os.path.basename(raster) for raster in os.listdir(result_dir)]
    conf_files = [
        os.path.join(classification_dir, conf_raster)
        for conf_raster in os.listdir(classification_dir)
        if conf_raster not in raster_list
        and "ConfMap" in conf_raster
        and conf_raster.replace("ConfMap", "Classified") in raster_names_list
    ]
    try:
        print("\nStarting post-processing algorithms")
        for index, raster in enumerate(raster_list):
            for conf in conf_files:
                if os.path.basename(raster).replace("Classified ", "") == os.path.basename(conf).replace(
                    "ConfMap ", ""
                ):
                    conf_raster = gdal.Open(conf, 1)
                    conf_raster_array = conf_raster.ReadAsArray().astype("float32")
                    raster_ = gdal.Open(raster, 1)
                    raster_array = raster_.ReadAsArray().astype("uint8")
                    month = get_month(filename=os.path.basename(raster))
                    mask = clauses(conf_arr=conf_raster_array, raster_arr=raster_array, month=month)
                    raster_array[mask == False] = 99
                    raster_.WriteArray(raster_array)
                    raster_, raster_array = None, None
                    conf_raster, conf_raster_array, mask = None, None, None
                    print(f"Successfully processed {index + 1} file", end="\n")
        rename_processed_files(result_dir=result_dir)
    except PermissionError as e:
        print("File from this folder is opened with another program.", e, sep="\n")
        sys.exit(1)


def clauses(conf_arr, raster_arr, month):
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
            np.logical_and(np.logical_and(conf_arr > 0.26, month == 8), raster_arr == 11),
            np.logical_and(np.logical_and(conf_arr > 0.47, month == 8), raster_arr == 13),
            np.logical_and(np.logical_and(conf_arr > 0.55, month == 8), raster_arr == 16),
            np.logical_and(np.logical_and(conf_arr > 0.45, month == 8), raster_arr == 21),
            np.logical_and(np.logical_and(conf_arr > 0.31, month == 8), raster_arr == 31),
            np.logical_and(np.logical_and(conf_arr > 0.25, month == 8), raster_arr == 41),
            np.logical_and(np.logical_and(conf_arr > 0.39, month == 8), raster_arr == 51),
            np.logical_and(np.logical_and(conf_arr > 0.25, month == 8), raster_arr == 61),
            np.logical_and(np.logical_and(conf_arr > 0.53, month == 8), raster_arr == 62),
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


def rename_processed_files(result_dir):
    src = [os.path.join(result_dir, file) for file in os.listdir(result_dir)]
    for file in src:
        dst = os.path.join(result_dir, os.path.basename(file).replace("Classified", "Processed"))
        os.rename(file, dst)


def clear_console():
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


if __name__ == "__main__":
    clear_console()
    print("Data post-processing algorithm", end="\n")
    rasters, data_directory = ask_for_files()
    postprocessing_folder = create_folder_for_results(working_dir=data_directory)
    copied_rasters = create_raster_copies(selected_files=rasters, result_dir=postprocessing_folder)
    post_processing(
        raster_list=copied_rasters,
        classification_dir=data_directory,
        result_dir=postprocessing_folder,
    )
