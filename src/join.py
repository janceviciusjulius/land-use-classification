import os
import shutil
import sys
import time
import datetime as dt
from pprint import pprint
from tkinter import filedialog
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo

from osgeo import gdal, ogr
from osgeo.gdalconst import GA_Update
from tkinter import *
from tkinter import Tk
import options


def joining_data(final_name, files_to_mosaic_path, path, shape_file_usage, shape_file):
    # Sentinel data joining method (J01)
    if shape_file_usage == 1:
        output_file_name = final_name + ".tiff"
        if os.path.isfile(os.path.join(path, output_file_name)):
            while True:
                boolean = str(input("File already exits. Do you want to continue? (Y/N) "))
                if boolean.lower() == "y":
                    os.remove(os.path.join(path, output_file_name))
                    break
                elif boolean.lower() == "n":
                    print("Request completed successfully.")
                    sys.exit(1)
                else:
                    print("\nError. Please specify an answer.\n")
        output_path = os.path.join(path, output_file_name)
        print("\nLinking process starts")
        gdal.Warp(
            output_path,
            files_to_mosaic_path,
            format="GTiff",
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES", "TILED=YES"],
                cutlineDSName=shape_file,
                dstNodata=0,
                cropToCutline=True,
                callback=progress_cb,
                callback_data=".",
            ),
        )
        print("End of linking process\n")
    elif shape_file_usage == 2:
        source = ogr.Open(shape_file)
        layer = source.GetLayer()
        schema = []
        ldefn = layer.GetLayerDefn()
        for n in range(ldefn.GetFieldCount()):
            fdefn = ldefn.GetFieldDefn(n)
            schema.append(fdefn.name)
        print("\nChoose field attribute name:")
        for i in range(len(schema)):
            print(f"{i + 1}. {schema[i]}")
        while True:
            try:
                attribute_number = int(input("\nEnter the index of the selected attribute name: "))
                while not 0 < attribute_number < len(schema) + 1:
                    clear_console()
                    print("No such selection.\n")
                    print("Choose field attribute name:")
                    for i in range(len(schema)):
                        print(f"{i + 1}. {schema[i]}")
                    attribute_number = int(input("\nEnter the index of the selected attribute name: "))
            except ValueError:
                clear_console()
                print("Invalid input format.\n")
                print("Choose field attribute name:")
                for i in range(len(schema)):
                    print(f"{i + 1}. {schema[i]}")
                continue
            else:
                break
        attribute_name = '"' + schema[attribute_number - 1] + '"'
        print(
            "If You are providing name (string data type) please add ' in the beginning and ending of the text. "
            "Example: 'Kauno marios'."
        )
        while True:
            attribute_value = input("Provide attribute value: ")
            if len(attribute_value) < 1:
                print("Error. Please provide attribute value:")
            else:
                break
        attribute_value_name = attribute_value.replace("'", "")
        output_file_name = final_name + " " + attribute_value_name + ".tiff"
        output_path = os.path.join(path, output_file_name)
        if os.path.isfile(os.path.join(path, output_file_name)):
            while True:
                boolean = str(input("File already exits. Do you want to continue? (Y/N) "))
                if boolean.lower() == "y":
                    os.remove(os.path.join(path, output_file_name))
                    break
                elif boolean.lower() == "n":
                    print("Request completed successfully.")
                    sys.exit(1)
                else:
                    print("\nError. Please specify an answer.\n")
        print("\nLinking process starts")
        gdal.Warp(
            output_path,
            files_to_mosaic_path,
            format="GTiff",
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES", "TILED=YES"],
                cutlineDSName=shape_file,
                cropToCutline=True,
                cutlineWhere=f"{attribute_name}={attribute_value}",
                callback=progress_cb,
                callback_data=".",
            ),
        )
        print("End of linking process\n")


def ask_for_shape_file_or_layer():
    # Asking if joined picture needs to be cut using some object from .shp or .gpkg borders.
    print("\nSelect cutting layer:")
    print(
        "     1. Use all ShapeFile\n"
        "     2. Use special area (object) from ShapeFile\n"
        "     3. Use all ShapeFiles from specified folder\n"
    )
    while True:
        try:
            shape_file_choice = int(input("Enter the index of selection: "))
            while not 0 < shape_file_choice < 4:
                clear_console()
                print("No such selection.")
                print("\nSelect cutting layer:")
                print(
                    "     1. Use all ShapeFile\n"
                    "     2. Use special area (object) from ShapeFile\n"
                    "     3. Use all ShapeFiles from specified folder\n"
                )
                shape_file_choice = int(input("Enter the index of selection:"))
        except ValueError:
            clear_console()
            print("Invalid input format.")
            print("\nSelect cutting layer:")
            print(
                "     1. Use all ShapeFile\n"
                "     2. Use special area (object) from ShapeFile\n"
                "     3. Use all ShapeFiles from specified folder\n"
            )
            continue
        else:
            break
    return shape_file_choice


def progress_cb(complete, message, cb_data):
    # progress bar
    if int(complete * 100) % 10 == 0:
        print(f"{complete * 100:.0f}", end="", flush=True)
    elif int(complete * 100) % 3 == 0:
        print(f"{cb_data}", end="", flush=True)
    if int(complete * 100) == 100:
        print(f"", end=" - done.\n", flush=True)


def clear_console():
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


def read_lines_from_text(filename):
    converted_list = []
    with open(filename) as f:
        lines = f.readlines()
        for i in lines:
            converted_list.append(i.strip())
    return converted_list


def create_folder_for_final_product(directory, folder_type, main_path, shp_name=None):
    if folder_type == "Classified":
        name_for_folder = directory.replace("Classified ", "Joined Classified ")
        name_for_file = directory.replace("Classified ", f"Joined Classified {shp_name} ")
    elif folder_type == "Cleaned":
        name_for_folder = directory.replace("Cleaned ", "Joined ")
        name_for_file = directory.replace("Cleaned ", f"Joined {shp_name} ")
    joined_folder = os.path.join(main_path, name_for_folder)
    try:
        os.mkdir(joined_folder)
    except (FileExistsError, FileNotFoundError):
        print("Folder is already created")
    return joined_folder, name_for_folder, name_for_file


def create_folder_for_joined_cloud(directory, parent_dir):
    cloud_folder = os.path.join(parent_dir, "Joined " + directory)
    try:
        os.mkdir(cloud_folder)
    except (FileExistsError, FileNotFoundError):
        print("Folder is already created")
    return cloud_folder


def delete_folder(dir_name):
    print("Deletion of unnecessary data begins. ")
    try:
        shutil.rmtree(dir_name)
    except (os.error, OSError, FileNotFoundError, NotADirectoryError):
        print("Data deletion error.")
    print("Data deletion successful\n")


def ask_for_deleting(working_dir_adr):
    while True:
        boolean = str(input("Do you want to delete the original data (Y/N)? "))
        if boolean.lower() == "y":
            delete_folder(working_dir_adr)
            break
        elif boolean.lower() == "n":
            print("The data is left in storage.\n")
            break
        else:
            print("\nError. Please specify an answer.")


def set_nodata_value(folder):
    # No data value setter
    classified_files = os.listdir(folder)
    os.chdir(folder)
    nodata = 0
    for file in classified_files:
        ras = gdal.Open(file, GA_Update)
        for i in range(1, ras.RasterCount + 1):
            ras.GetRasterBand(i).SetNoDataValue(nodata)
            ras = None
    print(f"NoData values set")


def join_cloud_files(
    chosen_directory,
    cloud_dir_address,
    cloud_dir_name,
    dest_folder,
    files_to_mosaic_names,
    shp_file=None,
    shp_folder_name=None,
):
    # Cloud layer joining method (J02)
    if chosen_directory.startswith("Cleaned"):
        files_to_cloud_mosaic = []
        cloud_mask_files = list(files_to_mosaic_names)
        files = os.listdir(cloud_dir_address)
        for i in range(len(cloud_mask_files)):
            for j in range(len(files)):
                if cloud_mask_files[i] == files[j].replace("Cloud ", ""):
                    path = os.path.join(cloud_dir_address, files[j])
                    files_to_cloud_mosaic.append(path)
        if shp_file is not None:
            filenameWithEXT = os.path.basename(shp_file).split(".")[0]
            output_path = os.path.join(dest_folder, "Joined " + filenameWithEXT + " " + cloud_dir_name + ".tiff")
        else:
            filenameWithEXT = shp_folder_name
            output_path = os.path.join(dest_folder, "Joined " + filenameWithEXT + " " + cloud_dir_name + ".tiff")
        print("Cloud linking process starts")
        gdal.Warp(
            output_path,
            files_to_cloud_mosaic,
            format="GTiff",
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE"],
                cutlineDSName=shp_file,
                dstNodata=0,
                callback=progress_cb,
                callback_data=".",
            ),
        )
        print("End of cloud linking process")
    elif chosen_directory.startswith("Classified"):
        files_to_cloud_mosaic = []
        cloud_mask_files = list(files_to_mosaic_names)
        for i in range(len(cloud_mask_files)):
            cloud_mask_files[i] = cloud_mask_files[i].replace("Classified Ground ", "")
        files = os.listdir(cloud_dir_address)
        for i in range(len(cloud_mask_files)):
            for j in range(len(files)):
                if cloud_mask_files[i] == files[j].replace("Cloud ", ""):
                    files_to_cloud_mosaic.append(os.path.join(cloud_dir_address, files[j]))
        output_path = os.path.join(dest_folder, "Joined " + cloud_dir_name + ".tiff")
        print("Cloud linking process starts")
        gdal.Warp(
            output_path,
            files_to_cloud_mosaic,
            format="GTiff",
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE"],
                cutlineDSName=shp_file,
                dstNodata=0,
                callback=progress_cb,
                callback_data=".",
            ),
        )
        print("End of cloud linking process\n")


def choose_shp_file_cut_cutting():
    # window where .shp or .gpkg file for cutting is chosen
    root = Tk()
    root.title("File Open Dialog")
    root.resizable(False, False)
    root.geometry("300x150")
    filetypes = (
        ("ESRI Shapefile", "*.shp"),
        ("GeoPackage", "*.gpkg"),
    )
    shp_filename = askopenfilename(title="Open a file", initialdir=options.path_to_shp_files, filetypes=filetypes)
    root.destroy()
    return shp_filename


def delete_all_not_raster_files(folder):
    # Sometimes, when data is loaded in QGIS (or any other GIS program) xml files are created. Some functions are
    # written to work with all files in folder. In that case removing xml saves program from mistakes.
    xml_files = [
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if not (filename.endswith(".tiff") or filename.endswith(".tif"))
    ]
    try:
        for file in xml_files:
            os.remove(file)
    except PermissionError:
        print(
            "At least one of the all .xml files are opened with another program. Please close the file and restart "
            "script."
        )
        sys.exit(1)


def choose_files_from_folder():
    # Usable data selecting window
    clear_console()
    print("Data joining/cropping algorithm", "Please choose file/files which You want to join/crop", sep="\n", end="\n")
    time.sleep(1)
    root = Tk()
    root.title("File Open Dialog")
    root.resizable(False, False)
    root.geometry("300x150")
    files_paths = filedialog.askopenfilenames(initialdir=options.return_path())
    root.destroy()
    files_paths = list(files_paths)
    file_names = []
    for i in range(len(files_paths)):
        file_names.append(os.path.basename(files_paths[i]))
    dir_address = os.path.dirname(files_paths[0])
    dir_name = os.path.basename(dir_address)
    cloud_dir_address = ""
    cloud_dir_name = ""
    if dir_name.startswith("Cleaned"):
        cloud_dir_address = dir_address.replace("Cleaned ", "Cloud ")
        cloud_dir_name = os.path.basename(cloud_dir_address)
    elif dir_name.startswith("Classified"):
        cloud_dir_address = dir_address.replace("Classified ", "Cloud ")
        cloud_dir_name = os.path.basename(cloud_dir_address)
    return dir_address, dir_name, files_paths, file_names, cloud_dir_address, cloud_dir_name


def select_shp_folder_for_automation():
    root = Tk()
    root.title("File Open Dialog")
    root.resizable(False, False)
    root.geometry("300x150")
    shp_folder_path = filedialog.askdirectory(initialdir=options.path_to_shp_files)
    root.destroy()
    shp_folder_name = os.path.basename(shp_folder_path)
    return shp_folder_path, shp_folder_name


def create_folder_for_automation(directory, folder_type, main_path, shp_folder_name):
    if folder_type == "Classified":
        name_for_folder = directory.replace("Classified ", f"Joined {shp_folder_name} Classified ")
    elif folder_type == "Cleaned":
        name_for_folder = directory.replace("Cleaned ", f"Joined {shp_folder_name} ")
    joined_folder = os.path.join(main_path, name_for_folder)
    try:
        os.mkdir(joined_folder)
    except (FileExistsError, FileNotFoundError):
        print("Folder is already created")
    return joined_folder, name_for_folder


def get_index_of_attributes_from_shp(schema):
    name_index, key_index, type_index = 0, 0, 0
    for key in schema:
        if key == options.ID_VALUE:
            id_index = schema.index(key)
        if key == options.NAME_VALUE:
            name_index = schema.index(key)
        if key == options.TYPE_VALUE:
            type_index = schema.index(key)
    return id_index, name_index, type_index


def join_crop_data_with_automation(shp_folder_path, folder, joined_folder_name, files_to_mosaic_paths):
    list_of_shp_files = [shp for shp in os.listdir(shp_folder_path) if shp.endswith(".shp") or shp.endswith(".gpkg")]
    list_of_shp_files_paths = [os.path.join(shp_folder_path, shp) for shp in list_of_shp_files]
    print("\nLinking process starts")
    for i, shp_file in enumerate(list_of_shp_files_paths):
        if ".gpkg" in os.path.basename(shp_file):
            driver = ogr.GetDriverByName("GPKG")
        else:
            driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(shp_file, 0)
        layer = dataSource.GetLayer()
        schema = []
        ldefn = layer.GetLayerDefn()
        for n in range(ldefn.GetFieldCount()):
            fdefn = ldefn.GetFieldDefn(n)
            schema.append(fdefn.name)
        values_list = []
        for feature in layer:
            temp = []
            for fieldDefn in schema:
                temp.append(feature.GetField(fieldDefn))
            values_list = temp
        water_body_ID_index, water_body_name_index, water_body_type_index = get_index_of_attributes_from_shp(schema)
        values_list = [str(element).replace(" ", "_") for element in values_list]
        name = (
            f"{joined_folder_name} {values_list[water_body_ID_index]} {values_list[water_body_name_index]}"
            f" {values_list[water_body_type_index]}.tiff"
        )
        file_name = os.path.join(folder, name)
        gdal.Warp(
            file_name,
            files_to_mosaic_paths,
            format="GTiff",
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES", "TILED=YES"],
                cutlineDSName=shp_file,
                cropToCutline=True,
                dstNodata=0,
                callback=progress_cb,
                callback_data=".",
            ),
        )
        print(f"Processed {i + 1} file")
    print("End of joining/cropping process", end="\n\n")


def run():
    start_time = time.time()
    clear_console()
    (
        working_dir_address,
        chosen_directory,
        files_to_mosaic_paths,
        files_to_mosaic_names,
        cloud_dir_address,
        chosen_cloud_directory,
    ) = choose_files_from_folder()
    shape_file_usage = ask_for_shape_file_or_layer()
    main_dir = os.path.dirname(working_dir_address)
    if shape_file_usage == 1 or shape_file_usage == 2:
        shape_file = choose_shp_file_cut_cutting()
        if chosen_directory.startswith("Cleaned"):
            joined_folder, final_name, file_name = create_folder_for_final_product(
                chosen_directory, "Cleaned", main_dir, os.path.basename(shape_file).split(".")[0]
            )
            # dest_joined_cloud_folder = create_folder_for_joined_cloud(chosen_cloud_directory, main_dir)
            delete_all_not_raster_files(joined_folder)
            joining_data(
                final_name=file_name,
                files_to_mosaic_path=files_to_mosaic_paths,
                path=joined_folder,
                shape_file_usage=shape_file_usage,
                shape_file=shape_file,
            )
            # join_cloud_files(chosen_directory=chosen_directory, cloud_dir_address=cloud_dir_address,
            #                  cloud_dir_name=chosen_cloud_directory, dest_folder=dest_joined_cloud_folder,
            #                  files_to_mosaic_names=files_to_mosaic_names, shp_file=shape_file)
        elif chosen_directory.startswith("Classified"):
            joined_folder, final_name, file_name = create_folder_for_final_product(
                chosen_directory, "Classified", main_dir, os.path.basename(shape_file).split(".")[0]
            )
            # dest_joined_cloud_folder = create_folder_for_joined_cloud(chosen_cloud_directory, main_dir)
            delete_all_not_raster_files(joined_folder)
            joining_data(
                final_name=file_name,
                files_to_mosaic_path=files_to_mosaic_paths,
                path=joined_folder,
                shape_file=shape_file,
                shape_file_usage=shape_file_usage,
            )
            # join_cloud_files(chosen_directory=chosen_directory, cloud_dir_address=cloud_dir_address,
            #                  cloud_dir_name=chosen_cloud_directory, dest_folder=dest_joined_cloud_folder,
            #                  files_to_mosaic_names=files_to_mosaic_names, shp_file=shape_file)
            set_nodata_value(joined_folder)
    elif shape_file_usage == 3:
        shp_folder_path, shp_folder_name = select_shp_folder_for_automation()
        if chosen_directory.startswith("Cleaned"):
            joined_folder, joined_folder_name = create_folder_for_automation(
                chosen_directory, "Cleaned", main_dir, shp_folder_name
            )
            join_crop_data_with_automation(shp_folder_path, joined_folder, joined_folder_name, files_to_mosaic_paths)
            # dest_joined_cloud_folder = create_folder_for_joined_cloud(chosen_cloud_directory, main_dir)
            # join_cloud_files(chosen_directory=chosen_directory, cloud_dir_address=cloud_dir_address,
            #                  cloud_dir_name=chosen_cloud_directory, dest_folder=dest_joined_cloud_folder,
            #                  files_to_mosaic_names=files_to_mosaic_names, shp_folder_name=shp_folder_name)
        elif chosen_directory.startswith("Classified"):
            joined_folder, joined_folder_name = create_folder_for_automation(
                chosen_directory, "Classified", main_dir, shp_folder_name
            )
            join_crop_data_with_automation(shp_folder_path, joined_folder, joined_folder_name, files_to_mosaic_paths)
            # dest_joined_cloud_folder = create_folder_for_joined_cloud(chosen_cloud_directory, main_dir)
            # join_cloud_files(chosen_directory=chosen_directory, cloud_dir_address=cloud_dir_address,
            #                  cloud_dir_name=chosen_cloud_directory, dest_folder=dest_joined_cloud_folder,
            #                  files_to_mosaic_names=files_to_mosaic_names, shp_folder_name=shp_folder_name)
            set_nodata_value(joined_folder)
    ask_for_deleting(working_dir_address)
    conversion = dt.timedelta(seconds=round(time.time() - start_time))
    print(f"Request completed successfully. Operating time: {str(conversion)}.")


if __name__ == "__main__":
    try:
        run()
    except PermissionError:
        print("File is already opened with another program.")
        sys.exit(1)
