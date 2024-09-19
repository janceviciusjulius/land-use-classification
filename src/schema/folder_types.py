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

    def __str__(self) -> str:
        return self.value


class FolderPrefix(str, Enum):
    DOWNLOAD = "SENTINEL-2"
    ZIP = "ZIP"
    MOVED = "MOVED"
    MERGED = "MERGED"
    CLEANED = "CLEANED"
    CLOUD = "CLOUD"
    JOINED = "JOINED"
    CLASSIFIED = "CLASSIFIED"

    def __str__(self) -> str:
        return self.value
