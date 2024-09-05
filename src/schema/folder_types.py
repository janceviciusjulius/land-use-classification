from enum import Enum


class FolderType(str, Enum):
    PARENT = "PARENT"
    DOWNLOAD = "DOWNLOAD"
    ZIP = "ZIP"
    MOVED = "MOVED"
    MERGED = "MERGED"
    CLEANED = "CLEANED"
    CLOUD = "CLOUD"
    JOINED = "JOINED"
    CLASSIFIED = "CLASSIFIED"


class FolderPrefix(str, Enum):
    DOWNLOAD = "Sentinel-2"
    ZIP = "ZIP"
    MOVED = "MOVED"
    MERGED = "MERGED"
    CLEANED = "CLEANED"
    CLOUD = "CLOUD"
    JOINED = "JOINED"
    CLASSIFIED = "CLASSIFIED"
