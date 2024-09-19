from typing import Dict, Optional, List, Any
from loguru import logger
from domain.shared import Shared
from schema.cropping_choice import CroppingChoice
from schema.folder_types import FolderType

from schema.metadata_types import ParametersJson


class Join:

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder()
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.cropping_choice: CroppingChoice = self._ask_for_cropping_choice()
        self.shape_file: Optional[str] = self._choose_shp_file()
        self.shape_file_name: Optional[str] = self.shared.get_shp_from_path(self.shape_file)
        self.result_file_name: str = self._create_result_filename()

    def join(self):
        self.shared.create_folder(path=self.folders[FolderType.JOINED])
        self.shared.delete_all_xml(dir_name=self.folders[FolderType.CLEANED])

        print("------------")
        print(self.cropping_choice)
        print(self.shape_file)
        print(self.shape_file_name)
        print(self.result_file_name)
        print("------------")

    def _create_result_filename(self) -> str:
        start_date, end_date = self.parameters[ParametersJson.START_DATE], self.parameters[ParametersJson.END_DATE]
        if self.cropping_choice == CroppingChoice.NONE:
            return f"{FolderType.JOINED} {start_date}..{end_date}"
        return f"{FolderType.JOINED} {self.shape_file_name} {start_date}..{end_date}"

    def _choose_shp_file(self) -> Optional[str]:
        if self.cropping_choice != CroppingChoice.NONE:
            return self.shared.choose_shp_from_folder()
        return None

    def _ask_for_cropping_choice(self) -> CroppingChoice:
        options: List[str] = [member.value for member in CroppingChoice]
        while True:
            self.shared.display_options(options=options)
            try:
                shape_file_choice = int(input("Enter the index of selection: "))
                if 1 <= shape_file_choice <= len(options):
                    return CroppingChoice(options[shape_file_choice - 1])
                else:
                    self.shared.clear_console()
                    logger.error("Invalid selection. Please choose a valid option.")
            except ValueError:
                self.shared.clear_console()
                logger.error("Invalid input. Please enter a number.")
