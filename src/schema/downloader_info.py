from enum import Enum


class DownloadInfo(str, Enum):
    FEATURES_INFO = "features_info"
    GENERAL_SIZE = "general_size"
    ONLINE_COUNT = "online_count"
    FEATURES = "features"

    def __str__(self) -> str:
        return self.value
