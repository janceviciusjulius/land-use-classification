import os

ID_folder_name = "ID"
path_to_ID_data_files = os.path.join(os.getcwd(), ID_folder_name)
program_files_folder_name = "ProgramFiles"
path_to_program_files = os.path.join(os.getcwd(), program_files_folder_name)
SHP_folder_name = "ShapeFiles"
path_to_shp_files = os.path.join(os.getcwd(), SHP_folder_name)
coordinates_for_data_searching = os.path.join(path_to_program_files, "map.geojson")
saving_folder_name = "Data"
path_to_data = os.path.join(os.getcwd(), saving_folder_name)

backup_folder_name = "Results_Backup"


# Variables used for join.py
#   We recommend not to change
path_to_program_files = os.path.join(os.getcwd(), program_files_folder_name)
# Changable values for join.py algorithm.
ID_VALUE = "KADASTROID"
NAME_VALUE = "PAVADINIMAS"
TYPE_VALUE = "Tipas.FPI"


# Variables used for categorization.py
FIRST_PERCENTILE_VALUE = 25
SECOND_PERCENTILE_VALUE = 50
THIRD_PERCENTILE_VALUE = 75
FOURTH_PERCENTILE_VALUE = 95


# Variables used for postprocessing.py
confidence_boundary = 0.5

path_to_training_ground_October = os.path.join(
    path_to_program_files, "training_ground_October.csv"
)
path_to_validation_ground_October = os.path.join(
    path_to_program_files, "validation_ground_October.csv"
)

path_to_training_ground_September = os.path.join(
    path_to_program_files, "training_ground_September.csv"
)
path_to_validation_ground_September = os.path.join(
    path_to_program_files, "validation_ground_September.csv"
)

path_to_training_ground_August = os.path.join(
    path_to_program_files, "training_ground_August.csv"
)
path_to_validation_ground_August = os.path.join(
    path_to_program_files, "validation_ground_August.csv"
)

path_to_training_ground_July = os.path.join(
    path_to_program_files, "training_ground_July.csv"
)
path_to_validation_ground_July = os.path.join(
    path_to_program_files, "validation_ground_July.csv"
)

path_to_training_ground_June = os.path.join(
    path_to_program_files, "training_ground_June.csv"
)
path_to_validation_ground_June = os.path.join(
    path_to_program_files, "validation_ground_June.csv"
)

path_to_training_ground_May = os.path.join(
    path_to_program_files, "training_ground_May.csv"
)
path_to_validation_ground_May = os.path.join(
    path_to_program_files, "validation_ground_May.csv"
)

path_to_training_ground_April = os.path.join(
    path_to_program_files, "training_ground_April.csv"
)
path_to_validation_ground_April = os.path.join(
    path_to_program_files, "validation_ground_April.csv"
)

path_to_training_ground_March = os.path.join(
    path_to_program_files, "training_ground_March.csv"
)
path_to_validation_ground_March = os.path.join(
    path_to_program_files, "validation_ground_March.csv"
)

#       WATER CLASSIFICATION
path_to_training_data_water_regression = os.path.join(
    path_to_program_files, "training_water_RG.csv"
)
path_to_training_data_water_classification = os.path.join(
    path_to_program_files, "training_water_CL.csv"
)

path_to_validation_data_water_regression = os.path.join(
    path_to_program_files, "validation_water_RG.csv"
)
path_to_validation_data_water_classification = os.path.join(
    path_to_program_files, "validation_water_CL.csv"
)

#       URBAN CLASSIFICATION
path_to_training_data_urban = os.path.join(path_to_program_files, "training_urban.csv")
path_to_validation_data_urban = os.path.join(
    path_to_program_files, "validation_urban.csv"
)

#       FOREST CLASSIFICATION
path_to_training_data_forest = os.path.join(
    path_to_program_files, "training_forest.csv"
)
path_to_validation_data_forest = os.path.join(
    path_to_program_files, "validation_forest.csv"
)

#   User_paths
mindaugas_path = os.path.join(path_to_data, "Mindaugas Gudas")
martynas_path = os.path.join(path_to_data, "Martynas Pankauskas")
ieva_path = os.path.join(path_to_data, "Ieva Ucinaviciute")
gediminas_path = os.path.join(path_to_data, "Gediminas Dudenas")
nijole_path = os.path.join(path_to_data, "Nijole Remeikaite-Nikiene")
zydrune_path = os.path.join(path_to_data, "Zydrune Lydeikaite")
julius_path = os.path.join(path_to_data, "Julius Jancevicius")


def return_path():
    user_name = os.getlogin()
    if "mindaugas" in user_name.lower():
        if os.path.exists(mindaugas_path):
            return mindaugas_path
    elif "martynas" in user_name.lower():
        if os.path.exists(martynas_path):
            return martynas_path
    elif "ieva" in user_name.lower():
        if os.path.exists(ieva_path):
            return os.path.join(ieva_path)
    elif "gediminas" in user_name.lower():
        if os.path.exists(gediminas_path):
            return gediminas_path
    elif "nijole" in user_name.lower():
        if os.path.exists(nijole_path):
            return nijole_path
    elif "zydrune" in user_name.lower():
        if os.path.exists(zydrune_path):
            return zydrune_path
    elif "julius" in user_name.lower():
        if os.path.exists(julius_path):
            return julius_path
    else:
        return path_to_data
