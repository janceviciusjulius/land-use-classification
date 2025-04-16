from enum import Enum


class FeatureFields(str, Enum):
    TITLE = "Title"
    TITLE_S = "title"
    CLOUD_COVER = "CloudCover"
    DATE = "Date"
    COORDINATES = "Coordinates"

    COORDINATES_S = "coordinates"
    ONLINE = "online"
    STATUS = "status"
    PROPERTIES = "properties"
    SIZE = "size"
    DOWNLOAD = "download"
    SERVICES = "services"
    START_DATE = "startDate"
    CLOUD_COVER_S = "cloudCover"
    QMLGEO = "gmlgeometry"

    GEOMETRY = "geometry"

    def __str__(self):
        return self.value
