import os.path
from typing import List

from osgeo import ogr
import sys
from loguru import logger

from domain.shared import Shared
from schema.algorithm import Algorithm
from schema.folder_types import FolderType
from schema.metadata_types import ParametersJson


class ValidShp:
    def __init__(self, shared: Shared):
        self.shared: Shared = shared
        self.files: List[str] = self.shared.choose_files_from_folder(algorithm=Algorithm.SHP_VALID)

    def validate_shp(self):
        for file in self.files:
            logger.info(f"Working with {os.path.basename(file)} file")
            shp_file = ogr.Open(file, 1)
            layer = shp_file.GetLayer()
            try:
                for feature in layer:
                    geom = feature.GetGeometryRef()
                    if not geom.IsValid():
                        feature.SetGeometry(geom.MakeValid())
                        layer.SetFeature(feature)
                        assert feature.GetGeometryRef().IsValid()
                layer.ResetReading()
                assert all(feature.GetGeometryRef().IsValid() for feature in layer)
            except AttributeError:
                logger.error("Cannot fix file. File do not have GeometryRef information")
                sys.exit(1)
        logger.warning("End of file correction")

