from enum import Enum


class RootFolders(str, Enum):
    SHP_FOLDER = "shape_files"
    DATA_FOLDER = "data"
    PROGRAM_FOLDER = "program_files"
