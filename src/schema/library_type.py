from enum import Enum


class LibraryType(Enum):
    TRAIN = "training"
    VALIDATION = "validation"

    def __str__(self) -> str:
        return self.value
