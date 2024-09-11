from enum import Enum

from pydantic import BaseModel
from typing import Any, Dict


class Metadata(str, Enum):
    PARAMETERS = "parameters"
    CLOUD_COVERAGE = "cloud_coverage"


class ParametersJson(str, Enum):
    INTERPOLATION = "interpolation"
    START_DATE = "start_date"
    END_DATE = "end_date"
    MAX_CLOUD_COVERAGE = "max_cloud_cover"
    FOLDERS = "folders"
    FILES = "files"


# class Parameters(BaseModel):
#     interpolation: bool
#     start_date: str
#     end_date: str
#     max_cloud_coverage: str | float
#     folders: Dict[str, Any]
#     files: Dict[str, Any]


class CloudCoverageJson(str, Enum):
    TITLE = "title"
    CLOUD = "cloud"
    DATE = "date"
    TILE = "tile"
    FILENAME = "filename"


# class CloudCoverage(BaseModel):
#     title: str
#     cloud: float
#     date: str
#     tile: str
#     filename: str
