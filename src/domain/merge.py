from typing import Optional, Dict

from domain.shared import Shared
from schema.folder_types import FolderType
from schema.metadata_types import Metadata


# TODO: CONTINUE WORKING ON MERGE REFACTORING
class Merge:
    def __init__(self, shared: Shared):
        self.shared = shared
        self.interpolation: Optional[bool] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        self.max_cloud_cover: Optional[int] = None
        self.folders: Optional[Dict[FolderType, str]] = None
        self.files: Dict[str | Metadata, str] = {}
