from enum import Enum


class Metadata(str, Enum):
    PARAMETERS = "parameters"
    CLOUD_COVERAGE = "cloud_coverage"

    def __str__(self) -> str:
        return self.value

class ParametersJson(str, Enum):
    INTERPOLATION = "interpolation"
    START_DATE = "start_date"
    END_DATE = "end_date"
    MAX_CLOUD_COVERAGE = "max_cloud_cover"
    FOLDERS = "folders"
    FILES = "files"

    def __str__(self) -> str:
        return self.value

class CloudCoverageJson(str, Enum):
    TITLE = "title"
    CLOUD = "cloud"
    DATE = "date"
    INTERVAL = "interval"
    TILE = "tile"
    FILENAME = "filename"

    def __str__(self) -> str:
        return self.value

