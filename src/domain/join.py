import time
from typing import Dict, Optional, List, Any

from domain.shared import Shared
from schema.folder_types import FolderType
import os

from schema.metadata_types import ParametersJson


class Join:

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder()
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.cropping_choice: type(Enum) = None

    def join(self):

