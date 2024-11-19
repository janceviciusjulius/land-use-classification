from enum import Enum


class ReadingType(str, Enum):
    INT16 = "int16"

    def __str__(self):
        return self.value
