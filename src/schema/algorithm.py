from enum import Enum


class Algorithm(str, Enum):
    DOWNLOAD = "download"
    MERGE = "merge"
    JOIN = "join"
    CLASSIFICATION = "classification"
    POST_PROCESSING = "post-processing"
    SHP_VALID = "shape validation"

    def __str__(self) -> str:
        return self.value
