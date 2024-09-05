from enum import Enum


class FolderType(str, Enum):
    PARENT = "PARENT"
    DOWNLOAD = "DOWNLOAD"
    ZIP = "ZIP"
    MOVED = "MOVED"
    MERGED = "MERGED"
    CLEANED = "CLEANED"
    CLASSIFIED = "CLASSIFIED"


class FolderTypePrefix(str, Enum):
    DOWNLOAD = "Sentinel-2"
