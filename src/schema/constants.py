from enum import Enum


class Constants(str, Enum):
    EMPTY_STRING = ""
    SPACE = " "

    NEW_LINE = "\n"
    LINE = "------------------------------------------------------"
    ACCURACIES_FILE = "models_accuracies.txt"

    STICKY = "ew"

    def __str__(self) -> str:
        return self.value
