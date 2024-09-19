from enum import Enum


class Constants(str, Enum):
    EMPTY_STRING = ""

    def __str__(self) -> str:
        return self.value
