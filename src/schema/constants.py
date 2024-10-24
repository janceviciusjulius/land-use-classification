from enum import Enum


class Constants(str, Enum):
    EMPTY_STRING = ""
    SPACE = " "

    STICKY = "ew"

    def __str__(self) -> str:
        return self.value
