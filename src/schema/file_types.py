from enum import Enum


class FileType(str, Enum):
    JP2 = ".jp2"
    TIFF = ".tiff"
    XML = ".xml"
    GPKG = ".gpkg"
    SHP = ".shp"

    MTD = "MTD"

    def __str__(self) -> str:
        return self.value
