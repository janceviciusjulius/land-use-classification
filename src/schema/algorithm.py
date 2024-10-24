from enum import Enum


class Algorithm(str, Enum):
    DOWNLOAD = "download"
    MERGE = "merge"
    JOIN = "join"
    CLASSIFICATION = "classification"

    def __str__(self) -> str:
        return self.value
