from enum import Enum


class CroppingChoice(str, Enum):
    ALL = "Use all ShapeFile"
    OBJECT = "Use special area (object) from ShapeFile"
    NONE = "Do not crop joined files"

    def __str__(self) -> str:
        return self.value
