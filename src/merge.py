import os
import shutil
import subprocess
import sys
import time
import datetime as dt
from collections import OrderedDict
from os.path import isdir
from tkinter import filedialog
from tkinter import *
from tkinter import Tk

import numpy as np
from bs4 import BeautifulSoup

import options
from osgeo import gdal

my_env = os.environ.copy()
otb_install_path = r"D:\Program Files\OTB-8.0.1-Win64"
# my_env["OTB_LOGGER_LEVEL"] = "CRITICAL"
my_env["CURRENT_SCRIPT_DIR"] = r"D:\Program Files\OTB-8.0.1-Win64"
my_env["PYTHONPATH"] = otb_install_path + r"\lib\python;" + (my_env.get("PYTHONPATH") or "")
my_env["OTB_APPLICATION_PATH"] = otb_install_path + r"\lib\otb\applications;" \
                                 + (my_env.get("OTB_APPLICATION_PATH") or "")
my_env["PATH"] = otb_install_path + r"\bin;" + my_env["PATH"]
my_env["GDAL_DATA"] = otb_install_path + "\share\data"
my_env["PROJ_LIB"] = otb_install_path + "\share\proj"
my_env["GDAL_DRIVER_PATH"] = "disable"
my_env["LC_NUMERIC"] = "C"


def get_info_of_existing_data():
    print("Data merge script for merging bands of downloaded satellite data into a single file.\n")
    print("Make sure that pictures are not opened with GDAL or any other program.")
    root = Tk()
    root.title('File Open Dialog')
    root.resizable(False, False)
    root.geometry('300x150')
    working_directory_address = filedialog.askdirectory(initialdir=options.path_to_data)
    root.destroy()
    chosen_dir_name = os.path.basename(working_directory_address)
    check_if_selected_correctly(chosen_dir_name)
    main_directory = os.path.dirname(working_directory_address)
    return working_directory_address, chosen_dir_name, main_directory


def prepare_path(directory):
    working_directory_address = directory
    chosen_dir_name = os.path.basename(working_directory_address)
    main_directory = os.path.dirname(working_directory_address)
    return working_directory_address, chosen_dir_name, main_directory


def check_if_selected_correctly(folder_name):
    if "Sentinel2" not in folder_name:
        print("Bad input files. Please re-run algorithm to change selection.")
        sys.exit(1)


def choose_ID_file_(main_dir_adr):
    main_folder_name = os.path.basename(main_dir_adr)
    ID_file_match = [file for file in os.listdir(options.path_to_ID_data_files) if file.startswith(main_folder_name)]
    ID_file = os.path.join(options.path_to_ID_data_files, ID_file_match[0])
    return ID_file


def choose_ID_file():
    # Choosing data's ID file
    root = Tk()
    root.title('File Open Dialog')
    root.resizable(False, False)
    root.geometry('300x150')
    ID_file = filedialog.askopenfilename(initialdir=options.return_path(), filetypes=[("Text files", ".txt")])
    root.destroy()
    return ID_file


def create_od_for_ID(ID_file):
    # Saving ID file content into OD variable
    od = OrderedDict()
    temp_list = read_lines_from_text(ID_file)
    for i in range(0, len(temp_list), 2):
        od[temp_list[i]] = temp_list[i + 1]
    return od


def delete_all_xml(dir_name):
    delete_xml = [band for band in os.listdir(dir_name) if band.endswith("xml") and not band.startswith("MTD")]
    for xml in delete_xml:
        os.remove(os.path.join(dir_name, xml))


def separate_bands_merging_for_one_package(working_dir_addr, merged_directory, ID_file, cloud_folder):
    # Finding and saving band paths. Merging them into one picture. Separating "Cloud" file too.
    global cloud_percentage
    files = os.listdir(working_dir_addr)
    number_of_folders = len(files)
    path_to_gdal = os.path.join(options.path_to_program_files, "gdal_merge.py")
    od = create_od_for_ID(ID_file)
    print("\nMerge process of the selected folder starts. Folders to merge:", number_of_folders)
    for i in range(1, number_of_folders + 1):
        temp_working_dir_name = os.path.join(working_dir_addr, files[i - 1])
        delete_all_xml(temp_working_dir_name)
        date = get_date_from_filename(temp_working_dir_name)
        for title, cloud_value in od.items():
            if files[i - 1].startswith(title):
                cloud_percentage = round(float(cloud_value), 3)
        try:
            output_file_name = os.path.join(os.getcwd(), options.saving_folder_name, merged_directory,
                                            (str(i) + ". " + date + " " + str(files[i - 1]).split("_")[5] +
                                             " " + str(cloud_percentage) + "%.tiff"))
            output_cloud_name = os.path.join(os.getcwd(), options.saving_folder_name, cloud_folder,
                                             (str(i) + ". " + "Cloud " + date + " " + str(files[i - 1]).split("_")[5] +
                                              " " + str(cloud_percentage) + "%.tiff"))
            output_cloud_name_20m = os.path.join(os.getcwd(), options.saving_folder_name, cloud_folder,
                                                 (str(i) + ". " + "Cloud " + date + " " +
                                                  str(files[i - 1]).split("_")[5] + " " +
                                                  str(cloud_percentage) + "%_20m.tiff"))
        except NameError:
            print("Data folder do not match with a selected ID file.")
            sys.exit(1)
        find_b2 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B02.jp2") or
                                                                                  filename.endswith("B02_10m.jp2"))]
        if len(find_b2) != 0:
            band_2 = os.path.join(os.getcwd(), temp_working_dir_name, find_b2[0])

        find_b3 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B03.jp2") or
                                                                                  filename.endswith("B03_10m.jp2"))]
        if len(find_b3) != 0:
            band_3 = os.path.join(os.getcwd(), temp_working_dir_name, find_b3[0])

        find_b4 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B04.jp2") or
                                                                                  filename.endswith("B04_10m.jp2"))]
        if len(find_b4) != 0:
            band_4 = os.path.join(os.getcwd(), temp_working_dir_name, find_b4[0])

        find_b5 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B05.jp2") or
                                                                                  filename.endswith("B05_20m.jp2"))]
        if len(find_b5) != 0:
            band_5 = os.path.join(os.getcwd(), temp_working_dir_name, find_b5[0])

        find_b6 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B06.jp2") or
                                                                                  filename.endswith("B06_20m.jp2"))]
        if len(find_b6) != 0:
            band_6 = os.path.join(os.getcwd(), temp_working_dir_name, find_b6[0])

        find_b7 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B07.jp2") or
                                                                                  filename.endswith("B07_20m.jp2"))]
        if len(find_b7) != 0:
            band_7 = os.path.join(os.getcwd(), temp_working_dir_name, find_b7[0])

        find_b8 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B08.jp2") or
                                                                                  filename.endswith("B08_10m.jp2"))]
        if len(find_b8) != 0:
            band_8 = os.path.join(os.getcwd(), temp_working_dir_name, find_b8[0])

        find_b8a = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B8A.jp2") or
                                                                                   filename.endswith("B8A_20m.jp2"))]
        if len(find_b8a) != 0:
            band_8A = os.path.join(os.getcwd(), temp_working_dir_name, find_b8a[0])

        find_b11 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B11.jp2") or
                                                                                   filename.endswith("B11_20m.jp2"))]
        if len(find_b11) != 0:
            band_11 = os.path.join(os.getcwd(), temp_working_dir_name, find_b11[0])

        find_b12 = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("B12.jp2") or
                                                                                   filename.endswith("B12_20m.jp2"))]
        if len(find_b12) != 0:
            band_12 = os.path.join(os.getcwd(), temp_working_dir_name, find_b12[0])

        find_SCL = [filename for filename in os.listdir(temp_working_dir_name) if (filename.endswith("SCL_20m.jp2"))]
        if len(find_SCL) != 0:
            band_SCL = os.path.join(os.getcwd(), temp_working_dir_name, find_SCL[0])

        find_xml = [filename for filename in os.listdir(temp_working_dir_name) if (filename.startswith("MTD") and
                                                                                   filename.endswith(".xml"))]
        if len(find_xml) != 0:
            xml_file = os.path.join(os.getcwd(), temp_working_dir_name, find_xml[0])
        gdal.Warp(output_cloud_name, band_SCL, format="GTiff",
                  options=gdal.WarpOptions(creationOptions=["COMPRESS=DEFLATE", "TILED=YES"], xRes=10, yRes=10,
                                           callback=progress_cb, callback_data='.'))
        gdal.Warp(output_cloud_name_20m, band_SCL, format="GTiff",
                  options=gdal.WarpOptions(creationOptions=["COMPRESS=DEFLATE", "TILED=YES"], xRes=20, yRes=20,
                                           callback=progress_cb, callback_data='.'))
        print("Successfully prepared", i, " file cloud files.")  # (M03)
        band_list = [band_4, band_3, band_2, band_5, band_6, band_7, band_8, band_8A, band_11, band_12]
        processed_bands = []
        for band in band_list:
            new_band_name = 'Processed ' + os.path.basename(band).replace(".jp2", ".tiff")
            output_file = os.path.join(os.getcwd(), temp_working_dir_name, new_band_name)
            if band in [band_4, band_3, band_2, band_8]:
                initiate_command = ["otbcli_BandMath", "-il", band, output_cloud_name,
                                    "-out", output_file, "int16",
                                    "-exp",
                                    '(im2b1 == 1 || im2b1 == 3 || im2b1 == 8 || im2b1 == 9 || im2b1 == 10 ||'
                                    ' im2b1 == 11) ? 0 : im1b1']
                subprocess.run(initiate_command, text=True, shell=True, capture_output=True, env=my_env)
            else:
                initiate_command = ["otbcli_BandMath", "-il", band, output_cloud_name_20m,
                                    "-out", output_file, "int16", "-exp",
                                    '(im2b1 == 1 || im2b1 == 3 || im2b1 == 8 || im2b1 == 9 || im2b1 == 10 ||'
                                    ' im2b1 == 11) ? 0 : im1b1']
                subprocess.run(initiate_command, text=True, shell=True, capture_output=True, env=my_env)
            processed_bands.append(output_file)
        merge_command = ["python", path_to_gdal, "-n", "0", "-a_nodata", "0", "-separate", "-o", output_file_name,
                         processed_bands[0], processed_bands[1], processed_bands[2], processed_bands[3],
                         processed_bands[4], processed_bands[5], processed_bands[6], processed_bands[7],
                         processed_bands[8], processed_bands[9], processed_bands[0], processed_bands[0],
                         processed_bands[0]]
        subprocess.call(merge_command, shell=True)
        print("Successfully merged ", i, "file.")  # (M01)
        for band in processed_bands:
            os.remove(band)
        # Checking images for offset value
        with open(xml_file, 'r') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, "xml")
        offset = bs_data.find_all("BOA_ADD_OFFSET")
        offset_values = [element.text for element in offset]
        if all(offset_values) and len(offset_values) > 0:
            offset_value = int(offset_values[0])
            raster = gdal.Open(output_file_name, 1)
            raster_array = raster.ReadAsArray()
            raster_array = raster_array + offset_value
            raster_array[raster_array < 0] = 0
            raster.WriteArray(raster_array)
            print(f"Successfully changed {i} file pixel values.", end="\n")
            raster, raster_array = None, None
    print("End of merging process\n")


def progress_cb(complete, message, cb_data):
    # Progress bar
    if int(complete * 100) % 10 == 0:
        print(f'{complete * 100:.0f}', end='', flush=True)
    elif int(complete * 100) % 3 == 0:
        print(f'{cb_data}', end='', flush=True)
    if int(complete * 100) == 100:
        print(f'', end=" - done.\n", flush=True)


def cleaning_data_background(merged_dir_address, cleaned_foldr):
    # Picture "cleaning", compressing and etc... (M02)
    files = os.listdir(merged_dir_address)
    number_of_folders = len(files)
    band_names = {1: "Band_4", 2: "Band_3", 3: "Band_2", 4: "Band_5", 5: "Band_6", 6: "Band_7", 7: "Band_8",
                  8: "Band_8A", 9: "Band_11", 10: "Band_12", 11: "NDTI", 12: "NDVIre", 13: "MNDWI"}
    print("Setting band names")
    for file in files:
        raster = gdal.Open(os.path.join(merged_dir_address, file), 1)
        number_of_bands = raster.RasterCount
        for band_number in range(number_of_bands):
            band = raster.GetRasterBand(band_number + 1)
            band.SetDescription(band_names[band_number + 1])
        raster = None
    print("Successfully set band names", end="\n\n")
    print("Data processing for the selected folder starts. Managed to process:", number_of_folders)
    for i in range(number_of_folders):
        gdal.Warp((os.path.join(os.getcwd(), cleaned_foldr, (files[i]))),
                  (os.path.join(os.getcwd(), merged_dir_address, files[i])),
                  format="GTiff",
                  options=gdal.WarpOptions(creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"], cropToCutline=True,
                                           dstNodata=0,
                                           callback=progress_cb, callback_data='.'))
        print(f"Processed {i + 1} file\n")
    print("End of file processing\n")


def get_date_from_filename(dir_address):
    # Date separator from filename
    number_of_files = len(os.listdir(dir_address))
    files = [file for file in os.listdir(dir_address) if not file.endswith(".xml") and not file.startswith("Processed")]
    if number_of_files > 0:
        date = (files[0])[7:15]
    else:
        print("There are no files in the folder.")
        sys.exit(1)
    return date


def create_folder_for_merged_data(chosen_dir_adr, parent_directory):
    merged_folder = os.path.join(parent_directory, "Merged " + chosen_dir_adr)
    try:
        os.mkdir(merged_folder)
    except (FileExistsError, FileNotFoundError):
        while True:
            boolean = str(input(f"\nSuch a folder ({os.path.basename(merged_folder)}) already exists."
                                f" Do you want to delete it (Y/N)? "))
            if boolean.lower() == "y":
                shutil.rmtree(merged_folder)
                time.sleep(1)
                os.mkdir(merged_folder)
                print("Folder deleted successfully.\n")
                break
            elif boolean.lower() == "n":
                print("End of program work")
                sys.exit(1)
            else:
                print("\nError. Please specify an answer.\n")
    return merged_folder


def create_folder_for_cleaned_data(chosen_dir_adr, parent_directory):
    cleaned_foldr = os.path.join(parent_directory, "Cleaned " + chosen_dir_adr)
    try:
        os.mkdir(cleaned_foldr)
    except (FileExistsError, FileNotFoundError):
        while True:
            boolean = str(input(f"Such a folder ({os.path.basename(cleaned_foldr)}) already exists. "
                                f"Do you want to delete it (Y/N)? "))
            if boolean.lower() == "y":
                shutil.rmtree(cleaned_foldr)
                time.sleep(1)
                os.mkdir(cleaned_foldr)
                print("Folder deleted successfully.\n")
                break
            elif boolean.lower() == "n":
                print("End of program work")
                sys.exit(1)
            else:
                print("\nError. Please specify an answer.\n")
    return cleaned_foldr


def create_folder_for_cloud_masks(chosen_dir_adr, parent_directory):
    cloud_folder = os.path.join(parent_directory, "Cloud " + chosen_dir_adr)
    try:
        os.mkdir(cloud_folder)
    except (FileExistsError, FileNotFoundError):
        while True:
            boolean = str(input(f"Such a folder ({os.path.basename(cloud_folder)})"
                                f" already exists. Do you want to delete it (Y/N)? "))
            if boolean.lower() == "y":
                shutil.rmtree(cloud_folder)
                time.sleep(1)
                os.mkdir(cloud_folder)
                print("Folder deleted successfully.")
                break
            elif boolean.lower() == "n":
                print("End of program work")
                sys.exit(1)
            else:
                print("\nError. Please specify an answer.\n")
    return cloud_folder


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)


def read_lines_from_text(filename):
    converted_list = []
    with open(filename) as f:
        lines = f.readlines()
        for i in lines:
            converted_list.append(i.strip())
    return converted_list


def delete_ID_file(ID_path):
    print("Deletion of the ID file begins. ")
    try:
        os.remove(ID_path)
    except (OSError, FileNotFoundError):
        print("Error deleting ID file.")
    print("ID file deleted successfully.\n")


def ask_for_deleting(dir_address, ID_path):
    while True:
        boolean = str(input("Do you want to delete the original data (Y/N)? "))
        if boolean.lower() == "y":
            delete_folder(dir_address)
            delete_ID_file(ID_path)
            break
        elif boolean.lower() == "n":
            print("The data is left in storage.\n")
            break
        else:
            print("\nError. Please specify an answer.")


def delete_folder(dir_name):
    print("Deletion of unnecessary data begins. ")
    try:
        shutil.rmtree(dir_name)
    except (os.error, OSError, FileNotFoundError, NotADirectoryError):
        print("Data deletion error.")
    print("Data deletion successful\n")


def only_numerics(string):
    seq_type = type(string)
    return float(seq_type().join(filter(seq_type.isdigit, string)))


def count_indexes(cleanedFolder):
    # band_names = {1: "Band_4", 2: "Band_3", 3: "Band_2", 4: "Band_5", 5: "Band_6", 6: "Band 7", 7: "Band 8",
    # 8: "Band 8A", 9: "Band 11", 10: "Band 12", 11: "NDTI", 12: "NDVIre", 13: "MNDWI"}
    print("Starting index counting process.")
    files = os.listdir(cleanedFolder)
    for index, file in enumerate(files):
        raster = gdal.Open(os.path.join(cleanedFolder, file), 1)
        band3 = raster.GetRasterBand(2).ReadAsArray()
        band4 = raster.GetRasterBand(1).ReadAsArray()
        band5 = raster.GetRasterBand(4).ReadAsArray()
        # band8 = raster.GetRasterBand(7).ReadAsArray()
        band11 = raster.GetRasterBand(9).ReadAsArray()
        band12 = raster.GetRasterBand(10).ReadAsArray()

        write_NDTI = raster.GetRasterBand(11)
        write_NDVIre = raster.GetRasterBand(12)
        write_MNDWI = raster.GetRasterBand(13)
        np.seterr(invalid='ignore')

        NDTI = ((band11 - band12) / (band11 + band12))
        NDTI = np.nan_to_num(NDTI)
        NDTI = np.around(NDTI, decimals=4)
        NDTI = NDTI * 10000
        NDTI = NDTI.astype("int16")
        write_NDTI.WriteArray(NDTI)

        NDVIre = (band5 - band4) / (band5 + band4)
        NDVIre = np.nan_to_num(NDVIre)
        NDVIre = np.around(NDVIre, decimals=4)
        NDVIre = NDVIre * 10000
        NDVIre = NDVIre.astype("int16")
        write_NDVIre.WriteArray(NDVIre)

        MNDWI = (band3 - band11) / (band3 + band11)
        MNDWI = np.nan_to_num(MNDWI)
        MNDWI = np.around(MNDWI, decimals=4)
        MNDWI = MNDWI * 10000
        MNDWI = MNDWI.astype("int16")
        write_MNDWI.WriteArray(MNDWI)

        raster, band3, band4, band5, band11, band12 = None, None, None, None, None, None
        print(f"Succesfully counted indexes for {index + 1} file", end="\n")
    print("End of index counting process", end="\n\n")


def get_lowest_cloud_percentage_file(files_list):
    current_min, current_file = 100.0, None
    for file in files_list:
        file_min = float(file.split(sep=" ")[-1].replace("%.tiff", ""))
        if current_min > file_min:
            current_min, current_file = file_min, file
    return current_file


def ask_for_interpolation():
    while True:
        boolean = str(input("Do you want to apply image interpolation (Y/N)? "))
        if boolean.lower() == "y":
            return True
        elif boolean.lower() == "n":
            print("Cloud interpolation algorithm is skipped.\n")
            return False
        else:
            print("\nError. Please specify an answer.")


def cloud_interpolation(merged_dir, apply_cloud_interpolation):
    if apply_cloud_interpolation:
        tiles = ['T34UDG', 'T34VDH', 'T34VEH', 'T34UEG', 'T34VFH', 'T34UFG', 'T34UFF', 'T34UFE', 'T34UGE', 'T34UEF',
                 'T35VLC', 'T35ULB', 'T35ULA', 'T35ULV', 'T35VMC', 'T35UMB', 'T35UMA']
        rasters_path = [os.path.join(merged_dir, raster) for raster in os.listdir(merged_dir)]
        for tile in tiles:
            chosen_rasters = []
            for raster_path in rasters_path:
                if tile in os.path.basename(raster_path):
                    chosen_rasters.append(raster_path)
            if len(chosen_rasters) == 0:
                print(f"No more rasters found for tile {tile}")
                continue
            chosen_rasters.sort(key=lambda x: float(x.split(sep=" ")[-1].replace("%.tiff", "")))
            chosen_rasters_basenames = [os.path.basename(chosen_raster) for chosen_raster in chosen_rasters]
            if len(chosen_rasters) > 1:
                for index, chosen_raster in enumerate(chosen_rasters[1:]):
                    best_raster = gdal.Open(chosen_rasters[0], 1)
                    best_raster_array = best_raster.ReadAsArray().astype('int16')
                    mask = (best_raster_array == 0)
                    if mask.all():
                        break
                    interpolation_raster = gdal.Open(chosen_raster, 1)
                    interpolation_raster_array = interpolation_raster.ReadAsArray().astype('int16')

                    best_raster_array[mask] = interpolation_raster_array[mask]
                    best_raster.WriteArray(best_raster_array)

                    best_raster, best_raster_array = None, None
                    interpolation_raster, interpolation_raster_array = None, None

                tile = chosen_rasters_basenames[0].split(" ")[2]
                date_ = (os.path.basename(os.path.dirname(os.path.abspath(chosen_rasters[0])))).split(" ")[2]
                os.rename(chosen_rasters[0], os.path.join(os.path.dirname(chosen_rasters[0]), f"{date_} {tile}.tiff"))
                print(f"Successfully extracted {tile} tile file.")
            else:
                tile = chosen_rasters_basenames[0].split(" ")[2]
                date_ = (os.path.basename(os.path.dirname(os.path.abspath(chosen_rasters[0])))).split(" ")[2]
                os.rename(chosen_rasters[0], os.path.join(os.path.dirname(chosen_rasters[0]), f"{date_} {tile}.tiff"))
        print("Cloud interpolation process completed successfully.", end="\n\n")
    else:
        print("Cloud interpolation is skipped.", end='\n')


def delete_files_after_cloud_interpolation(folder, apply_cloud_interpolation):
    if apply_cloud_interpolation:
        all_files = os.listdir(folder)
        files_to_delete = [os.path.join(folder, file) for file in all_files if len(file.split(" ")) == 4]
        print("Deleting files after cloud interpolation", end="\n")
        for file in files_to_delete:
            os.remove(file)
        print("Deleting process completed successfully.", end='\n\n')


# if __name__ == "__main__":
#     start_time = time.time()
#     clear_console()
#     working_dir_address, chosen_dir, main_dir = get_info_of_existing_data()
#     ID_file_path = choose_ID_file_(main_dir_adr=main_dir)
#     merged_dir = create_folder_for_merged_data(chosen_dir, main_dir)
#     cloud_directory = create_folder_for_cloud_masks(chosen_dir, main_dir)
#     separate_bands_merging_for_one_package(working_dir_address, merged_dir, ID_file_path, cloud_directory)
#     cleaned_folder = create_folder_for_cleaned_data(chosen_dir, main_dir)
#     # Possible interpolation place
#     cleaning_data_background(merged_dir, cleaned_folder)
#     count_indexes(cleanedFolder=cleaned_folder)
#     delete_folder(merged_dir)
#     ask_for_deleting(working_dir_address, ID_file_path)
#     conversion = dt.timedelta(seconds=round(time.time() - start_time))
#     print(f"Request completed successfully. Operating time: {str(conversion)}.")
