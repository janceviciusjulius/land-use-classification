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
    UNDERSCORE = "_"
    MINUS = "-"

    STICKY = "ew"

    TILES = "CartoDB positron"
    GECKO_DRIVER = "geckodriver.log"

    def __str__(self) -> str:
        return self.value


class ConstantValues(int, Enum):
    NO_DATA = 0
