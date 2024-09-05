import csv
import datetime as dt
import io
import logging
import os
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime
from os.path import isdir

import folium
import geopandas as gpd
import pandas as pd
from PIL import Image
from shapely import wkt

import login_info
import merge
import options
from cdse import CDSE


def unzipping_data(dir_name, zipped_dir_name):
    # Unzipping method (D02)
    files = os.listdir(dir_name)
    number_of_files = len(files)
    if number_of_files == 0:
        return 0
    print(f"Data unzipping begins. Number of files: {number_of_files}")
    for i in range(number_of_files):
        try:
            temp_file_path = os.path.join(dir_name, files[i])
            with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
                zip_ref.extractall(zipped_dir_name)
            print(f"Successfully unzipped {i + 1} file")
        except zipfile.BadZipfile:
            print(f"Due to downloaded file problem {i +1} file is skipped.")
            continue
    print("Unzipping complete.")


def request_analysis(info, size, available_count):
    # Counting available date from provided input parameters.
    print("\nData files found:", len(info))
    print("Size of the files:", size, "GB")
    print(
        f"Of the {len(info)} files, {available_count} are active and available,"
        f" {len(info) - available_count} are currently unavailable."
    )
    print(
        "NOTE: Unavailable data may become available during data download. If this happens, the data will be "
        "downloaded."
    )


def create_folder_for_download_sentinel2(start_time, end_time, max_cloud_cover, main_folder_path):
    dir_name = "Sentinel2 " + start_time + end_time + " " + "0" + "-" + str(max_cloud_cover) + "%"
    dir_name = os.path.join(main_folder_path, dir_name)
    os.mkdir(dir_name)
    return dir_name


def create_folder_for_program_files():
    path = os.path.join(os.getcwd(), options.program_files_folder_name)
    if not isdir(path):
        os.mkdir(path)
    return path


def create_folder_for_zipping(dir_name):
    zipped_dir_name = dir_name + " zipped"
    zipped_dir_name = os.path.join(data_folder, zipped_dir_name)
    os.mkdir(zipped_dir_name)
    return zipped_dir_name


def create_folder_for_bands(dir_name):
    band_folder = dir_name
    band_folder = os.path.join(os.getcwd(), options.saving_folder_name, band_folder)
    os.mkdir(band_folder)
    return band_folder


def create_folder_for_ID():
    path = os.path.join(os.getcwd(), options.ID_folder_name)
    if not isdir(path):
        os.mkdir(path)
    return path


def create_folder_for_SHP_files():
    path = os.path.join(os.getcwd(), options.SHP_folder_name)
    if not isdir(path):
        os.mkdir(path)
    return path


def create_folder_for_all_data():
    path = os.path.join(os.getcwd(), options.saving_folder_name)
    if not isdir(path):
        os.mkdir(path)
    return path


def clear_console():
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


def delete_folder(dir_name):
    # Method which deletes folder.
    print("\nDeletion of unnecessary data begins. ")
    try:
        shutil.rmtree(dir_name)
        print("Data deletion successful.")
    except (os.error, OSError, FileNotFoundError, NotADirectoryError):
        print("Data deletion error.")


def create_user_folder():
    for user in list(login_info.user_list.keys()):
        if not os.path.exists(os.path.join(options.saving_folder_name, user)):
            os.mkdir(os.path.join(options.saving_folder_name, user))


def login():
    while True:
        print("Sentinel-2 satellite data download algorithm.\n")
        print("Please choose an user:")
        for i, user in enumerate(list(login_info.user_list)):
            print(f"    {i + 1}. {user}")
        try:
            user_index = int(input("Specify an user index: "))
            if 0 < int(user_index) <= len((list(login_info.user_list))):
                username = login_info.user_list[list(login_info.user_list)[user_index - 1]][0]
                password = login_info.user_list[list(login_info.user_list)[user_index - 1]][1]
                api = CDSE((username, password))
                global CURRENT_USER
                CURRENT_USER = list(login_info.user_list.keys())[user_index - 1]
                create_user_folder()
                break
            else:
                clear_console()
                print(f"No index({user_index}) found.\n")
        except ValueError:
            clear_console()
            print("Bad data type! Please provide an integer.\n")
    return api


def form_feature_data(features):
    feature_info, general_size, online_num = {}, 0, 0
    for index, feature in enumerate(features):
        if feature["properties"]["status"].lower() == "online":
            online_num += 1
        title = feature["properties"]["title"]
        is_online = feature["properties"]["status"]
        feature_size = round(
            feature["properties"]["services"]["download"]["size"] / 1024 / 1024 / 1024,
            2,
        )
        general_size += feature_size
        feature_cloud_cover = round(feature["properties"]["cloudCover"], 2)
        coordinates = feature["geometry"]["coordinates"]
        qmlg = feature["properties"]["gmlgeometry"]
        date = feature["properties"]["startDate"][:10].replace("-", "")
        feature_info[title] = {
            "Title": title,
            "Date": date,
            "Status": is_online,
            "Size": feature_size,
            "CloudCover": feature_cloud_cover,
            "Coordinates": coordinates,
            "QMLGeometry": qmlg,
        }
    return feature_info, round(general_size, 2), online_num


def create_image_for_area_covered(search_result, dir_path):
    # Taking coordinates from images metadata, processing and showing covered area by query criteria.
    data = []
    for index, (key, value) in enumerate(search_result.items()):
        coordinate = value.get("Coordinates")[0]
        polygon_wkt = f"POLYGON (({' ,'.join(f'{x} {y}' for x, y in coordinate)}))"
        data.append(polygon_wkt)

    df = pd.DataFrame(data, columns=["geometry"])
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, crs="epsg:4326")
    try:
        m = folium.Map(location=[54.90942, 23.91456], zoom_start=7, tiles="CartoDB positron")
        for _, r in gdf.iterrows():
            sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.000001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
            geo_j.add_to(m)
        img_data = m._to_png(3)
        img = Image.open(io.BytesIO(img_data))
        img.save(os.path.join(dir_path, os.path.basename(dir_path + ".png")))
        img.show(os.path.join(dir_path, os.path.basename(dir_path + ".png")))
        if os.path.isfile("geckodriver.log"):
            try:
                os.remove("geckodriver.log")
            except PermissionError:
                pass
    except Exception as e:
        print(
            "Cannot create coverage photo due to server error. If coverage photo is necessary rerunning script should"
            "solve the problem",
            end="\n",
        )
        print(e)


def path_to_bands_sentinel2(zipped_dir_name, band_folder):
    # Taking only the necessary data (D03)
    files = os.listdir(zipped_dir_name)
    number_of_files = len(files)
    for i in range(number_of_files):
        temp_band_folder = os.path.join(band_folder, files[i])
        os.mkdir(temp_band_folder)
        # XML part
        dir_path = os.path.join(zipped_dir_name, files[i])
        dir_files = os.listdir(dir_path)
        for dir_file in dir_files:
            if dir_file.startswith("MTD") and dir_file.endswith(".xml"):
                shutil.copyfile(
                    os.path.join(dir_path, dir_file),
                    os.path.join(temp_band_folder, dir_file),
                )
        # End of XML part
        folder = os.path.join(zipped_dir_name, files[i], "GRANULE")
        data_name = os.listdir(folder)
        folder = os.path.join(folder, data_name[0], "IMG_DATA")
        img_data = os.listdir(folder)
        if len(img_data) != 3:
            for j in range(len(img_data)):
                band = os.path.join(folder, img_data[j])
                temp_band_folder = os.path.join(band_folder, files[i], img_data[j])
                shutil.copyfile(band, temp_band_folder)
        elif len(img_data) == 3:
            folders = os.listdir(folder)
            for j in range(len(folders)):
                path_to_folders = os.path.join(folder, folders[j])
                img_data = os.listdir(path_to_folders)
                for z in range(len(img_data)):
                    band = os.path.join(path_to_folders, img_data[z])
                    temp_band_folder = os.path.join(band_folder, files[i], img_data[z])
                    shutil.copyfile(band, temp_band_folder)
        print("Moved", i + 1, "file.")
    print("Band exclusion complete.")


def save_downloaded_files_id(features, start_time, end_time, max_cloud):
    filename = start_time + ".." + end_time + " " + "0" + "-" + str(max_cloud) + "%.txt"
    path = os.path.join(os.getcwd(), options.ID_folder_name, filename)
    for feature in features:
        title = features[feature]["Title"]
        cloud = features[feature]["CloudCover"]
        with open(path, "a") as f:
            f.write(title + "\n")
            f.write(str(cloud) + "\n")
            f.close()
    print("\nDownloaded data ID saved.\n")


def download_data(api, features, feature_info, dir_name, start_date, end_date, max_cloud):
    # Available data downloading, creating folders, unzipping and required data extraction
    while True:
        boolean = input("\nDo you want to download the data (Y/N)? ")
        if boolean.lower() == "y":
            interpolation = merge.ask_for_interpolation()
            print("\nStarting downloading")
            # downloaded_list, lta_list, error_list = downloading_progress(products, dir_name)
            downloaded_list = api.download_features(features, dir_name)
            time.sleep(1)
            save_downloaded_files_id(
                features=feature_info,
                start_time=start_date,
                end_time=end_date,
                max_cloud=max_cloud,
            )
            print(f"Data download complete. Of the {len(features)} files, {len(downloaded_list)} were downloaded.")
            print(f"Due to the server errors {len(features) - len(downloaded_list)} files could not be downloaded.")
            zipped_dir_name = create_folder_for_zipping(dir_name)
            unzipping_data(dir_name, zipped_dir_name)
            delete_folder(dir_name)
            time.sleep(1.5)
            band_folder = create_folder_for_bands(dir_name)
            path_to_bands_sentinel2(zipped_dir_name, band_folder)
            delete_folder(zipped_dir_name)
            print(f"INTERPOLATION: {interpolation}")
            return interpolation
        elif boolean.lower() == "n":
            print("The data download phase is skipped.")
            parent_path = os.path.dirname(dir_name)
            if len(os.listdir(parent_path)) == 2:
                shutil.rmtree(parent_path)
            else:
                shutil.rmtree(dir_name)
            sys.exit(1)
        else:
            print("\nError. Please specify an answer.")


def data_from_sentinel(api):
    # Getting inputs (date interval and cloud cover interval)
    zemaitija = ["34UDG", "34VDH", "34UEG", "34VEH"]
    aukstaitija = ["34VFH", "34UFG", "35VLC", "35ULB", "35UMB", "35VMC"]
    apacia = ["34UFF", "34UFE", "35ULA", "34UGE", "35ULV", "35UMA", "35UMV"]
    footprint = zemaitija + aukstaitija + apacia
    print("\nThe map of Lithuania has been read.\n")
    print("Sentinel-2 2A data is available from 2018 March.\n")

    start_time = input("Specify a search start date (YYYY-MM-DD): ")
    end_time = input("Specify a search finish date (YYYY-MM-DD): ")
    while (
        (end_time < start_time)
        or (end_time > datetime.now().strftime("%Y-%m-%d"))
        or (len(start_time) != 10)
        or (len(end_time) != 10)
    ):
        clear_console()
        print("Bad interval. Please re-enter the date:\n")
        start_time = input("Specify a search start date (YYYY-MM-DD): ")
        end_time = input("Specify a search finish date (YYYY-MM-DD): ")
    clear_console()
    while True:
        try:
            max_cloud_cover = int(input("Specify a maximum percentage of cloud cover (0%-100%): "))
            while not (0 <= max_cloud_cover <= 100):
                clear_console()
                print("The specified maximum cloud percentage is out of range or is smaller than minimum range.")
                max_cloud_cover = int(input("\nSpecify a maximum percentage of cloud cover (0%-100%):"))
        except ValueError:
            clear_console()
            print("Invalid input format.\n")
            continue
        else:
            break
    api.set_collection("Sentinel2")
    api.set_processing_level("S2MSI2A")

    footprint = CDSE.process_footprint(footprint)
    features = api.query(
        start_date=start_time,
        end_date=end_time,
        footprint=footprint,
        cloudcover=max_cloud_cover,
        max_records=None,
    )
    features_info, general_size, online_count = form_feature_data(features=features)
    download_process = False
    if len(features_info) == 0:
        print("\nNo data was found according to the given criteria. Please try again providing different criteria.")
        features_info, features = None, None
        data_from_sentinel(api=api)
    else:
        download_process = True
    if download_process:
        main_folder_name = start_time + ".." + end_time + " " + "0" + "-" + str(max_cloud_cover) + "%"
        main_folder_path = os.path.join(data_folder, CURRENT_USER, main_folder_name)
        if not isdir(main_folder_path):
            os.mkdir(main_folder_path)
            """
            
            """
        if not isdir(
            os.path.join(
                main_folder_path,
                ("Sentinel2 " + start_time + ".." + end_time + " " + "0" + "-" + str(max_cloud_cover) + "%"),
            )
        ):
            dir_name = create_folder_for_download_sentinel2(start_time, end_time, max_cloud_cover, main_folder_path)
            request_analysis(info=features_info, size=general_size, available_count=online_count)
            create_image_for_area_covered(features_info, main_folder_path)
            interpolation = download_data(
                api=api,
                features=features,
                feature_info=features_info,
                dir_name=dir_name,
                start_date=start_time,
                end_date=end_time,
                max_cloud=max_cloud_cover,
            )
        else:
            print("\nThe same data folder exists. You can delete the folder to download the data again.")
            while True:
                print("NOTE: All downloaded and pre-processed data will be deleted.")
                boolean = str(input("Do you want to delete the data (Y/N)? "))
                if boolean.lower() == "y":
                    raw_data_folder = (
                        "Sentinel2 " + start_time + ".." + end_time + " " + "0" + "-" + str(max_cloud_cover) + "%"
                    )
                    if os.path.exists(os.path.join(main_folder_path, "Cleaned " + raw_data_folder)):
                        shutil.rmtree(os.path.join(main_folder_path, "Cleaned " + raw_data_folder))
                    if os.path.exists(os.path.join(main_folder_path, "Merged " + raw_data_folder)):
                        shutil.rmtree(os.path.join(main_folder_path, "Merged " + raw_data_folder))
                    if os.path.exists(os.path.join(main_folder_path, "Cloud " + raw_data_folder)):
                        shutil.rmtree(os.path.join(main_folder_path, "Cloud " + raw_data_folder))
                    delete_folder(os.path.join(main_folder_path, raw_data_folder))
                    time.sleep(1)
                    dir_name = create_folder_for_download_sentinel2(
                        start_time, end_time, max_cloud_cover, main_folder_path
                    )
                    request_analysis(
                        info=features_info,
                        size=general_size,
                        available_count=online_count,
                    )
                    create_image_for_area_covered(features_info, main_folder_path)
                    # interpolation = merge.ask_for_interpolation()
                    interpolation = download_data(
                        api=api,
                        features=features,
                        feature_info=features_info,
                        dir_name=dir_name,
                        start_date=start_time,
                        end_date=end_time,
                        max_cloud=max_cloud_cover,
                    )
                    break
                elif boolean.lower() == "n":
                    print("The data is left on disk.\n")
                    break
                else:
                    print("\nError. Please specify an answer.")
        print(
            "\nData downloading is completed. Data pre-processing is going to start.",
            end="\n",
        )
        download_process = False
        print(dir_name, interpolation)
        return dir_name, interpolation


if __name__ == "__main__":
    # Preparation
    program_start_time = time.time()
    create_folder_for_SHP_files()
    data_folder = create_folder_for_all_data()
    program_files_folder = create_folder_for_program_files()
    ID_data_folder = create_folder_for_ID()
    clear_console()
    # Downloading part
    api_obj = login()
    dir_path, interpolation_bool = data_from_sentinel(api=api_obj)
    # Merge part
    # working_dir_address, chosen_dir, main_dir = merge.prepare_path(dir_path)
    # ID_file_path = merge.choose_ID_file_(main_dir_adr=main_dir)
    # merged_dir = merge.create_folder_for_merged_data(chosen_dir, main_dir)
    # cloud_directory = merge.create_folder_for_cloud_masks(chosen_dir, main_dir)
    # merge.separate_bands_merging_for_one_package(working_dir_address, merged_dir, ID_file_path, cloud_directory)
    # cleaned_folder = merge.create_folder_for_cleaned_data(chosen_dir, main_dir)
    # merge.cleaning_data_background(merged_dir, cleaned_folder)
    # merge.cloud_interpolation(cleaned_folder, interpolation_bool)
    # merge.delete_files_after_cloud_interpolation(cleaned_folder, interpolation_bool)
    # merge.count_indexes(cleanedFolder=cleaned_folder)
    # merge.delete_folder(merged_dir)
    # merge.ask_for_deleting(working_dir_address, ID_file_path)
    # conversion = dt.timedelta(seconds=round(time.time() - program_start_time))
