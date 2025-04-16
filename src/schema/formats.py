from enum import Enum


class Format(str, Enum):
    GTIFF = "GTiff"

    def __str__(self):
        return self.value
