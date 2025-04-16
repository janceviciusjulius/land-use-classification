from enum import Enum


class UnitType(str, Enum):
    FILE = "file"
    PACKAGE = "package"

    def __str__(self) -> str:
        return self.value
