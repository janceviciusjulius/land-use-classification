from enum import Enum


class RootFolders(str, Enum):
    SHP_FOLDER = "shape_files"
    DATA_FOLDER = "data"
    PROGRAM_FOLDER = "program_files"
    LEARNING_FOLDER = "learning_data"
    MODEL_FOLDER = "models"

    def __str__(self) -> str:
        return self.value
