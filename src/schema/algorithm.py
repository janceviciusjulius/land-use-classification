from enum import Enum


class Algorithm(str, Enum):
    DOWNLOAD = "download"
    MERGE = "merge"
    JOIN = "join"
    CLASSIFICATION = "classification"
    POST_PROCESSING = "post-processing"

    def __str__(self) -> str:
        return self.value
