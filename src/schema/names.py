from enum import Enum


class Name(str, Enum):
    TITLE = "Lithuanian Satellite Data Classifier"
    FONT = "Lucida 14 bold"
    CHOOSE = "Choose an algorithm"

    DOWNLOAD = "Download Sentinel Data"
    JOIN = "Join/Crop"
    CLASSIFICATION = "Data Classification"
    POST_PROCESSING = "Post Processing"
    SHP_VALID = "ShapeFile Validation"
    CLOSE = "Close program"
