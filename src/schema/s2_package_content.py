from enum import Enum


class PackageContent(str, Enum):
    GRANULE = "GRANULE"
    IMG_DATA = "IMG_DATA"

    def __str__(self) -> str:
        return self.value
