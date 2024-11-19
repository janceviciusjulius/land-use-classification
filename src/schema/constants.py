from enum import Enum


class Constants(str, Enum):
    EMPTY_STRING = ""
    SPACE = " "
    DOT = "."
    NEW_LINE = "\n"
    LINE = "------------------------------------------------------"
    ACCURACIES_FILE = "models_accuracies.txt"
    QUOTE = '"'
    SMALL_QUOTE = "'"

    STICKY = "ew"

    def __str__(self) -> str:
        return self.value


class ConstantValues(int, Enum):
    NO_DATA = 0
