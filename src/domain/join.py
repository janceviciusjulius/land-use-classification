import os.path
from typing import Any, Dict, List, Optional

from loguru import logger
from osgeo import gdal, ogr
from osgeo.ogr import DataSource, Layer

from additional.logger_configuration import configurate_logger
from domain.shared import Shared
from schema.algorithm import Algorithm
from schema.constants import Constants, ConstantValues
from schema.cropping_choice import CroppingChoice
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.formats import Format
from schema.metadata_types import ParametersJson

configurate_logger()


class Join:
    CREATION_OPTIONS: List[str] = ["COMPRESS=DEFLATE", "BIGTIFF=YES"]

    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder(algorithm=Algorithm.JOIN)
        self.parameters: Dict[str, Any] = self.shared.get_parameters(files_paths=self.files)
        self.folders: Dict[FolderType, str] = self.parameters[ParametersJson.FOLDERS]
        self.cropping_choice: CroppingChoice = self._ask_for_cropping_choice()
        self.shape_file: Optional[str] = self._choose_shp_file()
        self.shape_file_name: Optional[str] = self.shared.get_shp_from_path(self.shape_file)
        self.result_file_name: str = self._create_result_filename()
        self.result_file_path: Optional[str] = None

    def join(self):
        self.shared.create_folder(path=self.folders[FolderType.JOINED])
        self.shared.delete_all_xml(dir_name=self.folders[FolderType.CLEANED])

        if self.cropping_choice == CroppingChoice.ALL:
            self.result_file_name: str = self.shared.add_file_ext(file_name=self.result_file_name, ext=FileType.TIFF)
            self.result_file_path: str = os.path.join(self.folders[FolderType.JOINED], self.result_file_name)
            self.shared.check_if_file_exists(path=self.result_file_path)
            return self._join_all()

        elif self.cropping_choice == CroppingChoice.OBJECT:
            shp_schema: List[str] = self._get_keys_from_shp()
            key_index = self.shared.select_from_list_ui(objects=shp_schema)
            attribute_name: str = Constants.QUOTE + shp_schema[key_index] + Constants.QUOTE
            self._input_info()
            attribute_value: str = self.shared.ask_for_input()

            self.result_file_name: str = (
                self.result_file_name
                + Constants.SPACE
                + attribute_value.replace(Constants.SMALL_QUOTE, Constants.EMPTY_STRING)
            )
            self.result_file_name: str = self.shared.add_file_ext(file_name=self.result_file_name, ext=FileType.TIFF)
            self.result_file_path: str = os.path.join(self.folders[FolderType.JOINED], self.result_file_name)
            self.shared.check_if_file_exists(path=self.result_file_path)

            clause: str = f"{attribute_name}={attribute_value}"
            return self._join_object(clause=clause)

        elif self.cropping_choice == CroppingChoice.NONE:
            self.result_file_name: str = self.shared.add_file_ext(file_name=self.result_file_name, ext=FileType.TIFF)
            self.result_file_path: str = os.path.join(self.folders[FolderType.JOINED], self.result_file_name)
            self.shared.check_if_file_exists(path=self.result_file_path)
            return self._join_none()

    @staticmethod
    def _input_info() -> None:
        print(
            "If You are providing name (string data type) please add ' in the beginning and ending of the text. "
            "Example: 'Kauno HE Tvenkinys'."
        )

    def _get_keys_from_shp(self) -> List[str]:
        source: DataSource = ogr.Open(self.shape_file)
        layer: Layer = source.GetLayer()
        schema: List[str] = []
        layer_defn = layer.GetLayerDefn()
        for n in range(layer_defn.GetFieldCount()):
            key_defn = layer_defn.GetFieldDefn(n)
            schema.append(key_defn.name)
        return schema

    def _join_none(self):
        gdal.Warp(
            self.result_file_path,
            self.files,
            format=Format.GTIFF,
            options=gdal.WarpOptions(
                creationOptions=self.CREATION_OPTIONS,  # "TILED=YES"
                cropToCutline=True,
                callback=self.shared.progress_cb,
                callback_data=Constants.DOT,
            ),
        )

    def _join_object(self, clause: str):
        gdal.Warp(
            self.result_file_path,
            self.files,
            format=Format.GTIFF,
            options=gdal.WarpOptions(
                creationOptions=self.CREATION_OPTIONS,  # "TILED=YES"
                cutlineDSName=self.shape_file,
                cropToCutline=True,
                cutlineWhere=clause,
                callback=self.shared.progress_cb,
                callback_data=Constants.DOT,
            ),
        )

    def _join_all(self) -> None:
        gdal.Warp(
            self.result_file_path,
            self.files,
            format=Format.GTIFF,
            options=gdal.WarpOptions(
                creationOptions=self.CREATION_OPTIONS,  # "TILED=YES"
                cutlineDSName=self.shape_file,
                dstNodata=ConstantValues.NO_DATA,
                cropToCutline=True,
                callback=self.shared.progress_cb,
                callback_data=Constants.DOT,
            ),
        )

    def _create_result_filename(self) -> str:
        start_date, end_date = (
            self.parameters[ParametersJson.START_DATE],
            self.parameters[ParametersJson.END_DATE],
        )
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
