import os
from typing import Optional, Dict, List, Union, Tuple
from loguru import logger
from os import listdir
from osgeo import gdal
import numpy as np
import rasterio

from domain.shared import Shared
from exceptions.exceptions import InvalidParameterException
from schema.band_types import BandType, AddBandType
from schema.folder_types import FolderType
from schema.metadata_types import Metadata, ParametersJson, CloudCoverageJson


# TODO: CONTINUE WORKING ON MERGE REFACTORING
class Merge:
    GDAL_MERGE: str = "gdal_merge.py"

    def __init__(
        self,
        shared: Shared,
        interpolation: bool,
        start_date: str,
        end_date: str,
        max_cloud_cover: int,
        folders: [Dict[FolderType, str]],
        files: Dict[str | Metadata, str],
    ):
        self.shared: Shared = shared
        self.interpolation: bool = interpolation
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.max_cloud_cover: int = max_cloud_cover
        self.folders: [Dict[FolderType, str]] = folders
        self.files: Dict[str | Metadata, str] = files

    def process_data(self):
        logger.info("Starting merging...")
        self._create_folders()
        self._merge()

    def _merge(self):
        files_information: Dict[str, float] = self.shared.read_json(path=self.files[Metadata.CLOUD_COVERAGE])
        files: List[str] = listdir(self.folders[FolderType.DOWNLOAD])
        logger.info(f"Merge process of the selected folder starts. Folders to merge: {len(files)}")

        for index, file in enumerate(files):
            temp_working_dir_name: str = os.path.join(self.folders[FolderType.DOWNLOAD], file)
            self.shared.delete_all_xml(temp_working_dir_name)

            cloud_percentage: float = files_information[file][CloudCoverageJson.CLOUD]
            date: str = files_information[file][CloudCoverageJson.DATE]
            tile: str = files_information[file][CloudCoverageJson.TILE]

            out_filename: str = os.path.join(
                self.folders[FolderType.MERGED], f"{index+1}. {date} {tile} {cloud_percentage}%.tiff"
            )
            cloud_10_filename: str = os.path.join(
                self.folders[FolderType.CLOUD], f"{index+1}. Cloud {date} {tile} {cloud_percentage}%.tiff"
            )
            cloud_20_filename = os.path.join(
                self.folders[FolderType.CLOUD], f"{index+1}. Cloud {date} {tile} {cloud_percentage}%_20m.tiff"
            )

            b2: str = self._match_band(band_type=BandType.B2, tile_folder=temp_working_dir_name)
            b3: str = self._match_band(band_type=BandType.B3, tile_folder=temp_working_dir_name)
            b4: str = self._match_band(band_type=BandType.B4, tile_folder=temp_working_dir_name)
            b5: str = self._match_band(band_type=BandType.B5, tile_folder=temp_working_dir_name)
            b6: str = self._match_band(band_type=BandType.B6, tile_folder=temp_working_dir_name)
            b7: str = self._match_band(band_type=BandType.B7, tile_folder=temp_working_dir_name)
            b8: str = self._match_band(band_type=BandType.B8, tile_folder=temp_working_dir_name)
            b8a: str = self._match_band(band_type=BandType.B7, tile_folder=temp_working_dir_name)
            b11: str = self._match_band(band_type=BandType.B11, tile_folder=temp_working_dir_name)
            b12: str = self._match_band(band_type=BandType.B12, tile_folder=temp_working_dir_name)

            scl: str = self._match_band(band_type=AddBandType.SCL, tile_folder=temp_working_dir_name)
            xml: str = self._match_band(band_type=AddBandType.XML, tile_folder=temp_working_dir_name)

            gdal.Warp(
                destNameOrDestDS=cloud_10_filename,
                srcDSOrSrcDSTab=scl,
                format="GTiff",
                options=gdal.WarpOptions(
                    creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
                    xRes=10,
                    yRes=10,
                    callback=self.shared.progress_cb,
                    callback_data=".",
                ),
            )
            gdal.Warp(
                destNameOrDestDS=cloud_20_filename,
                srcDSOrSrcDSTab=scl,
                format="GTiff",
                options=gdal.WarpOptions(
                    creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
                    xRes=10,
                    yRes=10,
                    callback=self.shared.progress_cb,
                    callback_data=".",
                ),
            )
            logger.info(f"Successfully prepared {index+1} file cloud files.")
            band_list: Tuple[str, ...] = (b4, b3, b2, b5, b6, b7, b8, b8a, b11, b12)
            for band_path in band_list:
                file_name: str = os.path.basename(band_path).replace(".jp2", ".tiff")
                new_band_name: str = f"Processed {file_name}"
                output_path: str = os.path.join(temp_working_dir_name, new_band_name)
                self._remove_clouds(scl_band=cloud_10_filename, band=band_path, output_path=output_path)


    def _remove_clouds(self, scl_band: str, band: str, output_path: str):
        values_to_check: List[int] = [1, 3, 8, 9, 10, 11]

        with rasterio.open(scl_band) as second_raster:
            second_band = second_raster.read(1)
            with rasterio.open(band) as first_raster:
                profile = first_raster.profile
                modified_layers = []

                # Iterate through each layer in the first raster
                for i in range(1, first_raster.count + 1):  # `count` gives the number of layers
                    # Read each layer from the first raster
                    first_band = first_raster.read(i)

                    # Apply the condition: set pixels to 0 where second raster has values in the list
                    first_band = np.where(np.isin(second_band, values_to_check), 0, first_band)

                    # Add the modified band to the list
                    modified_layers.append(first_band)

                # Update the profile (if necessary, you can adjust datatype, etc.)
                profile.update(dtype=rasterio.float32)

                # Write the modified layers to a new raster file
                with rasterio.open(output_path, 'w', **profile) as dst:
                    for idx, layer in enumerate(modified_layers, 1):  # Layers are 1-indexed
                        dst.write(layer, idx)


    def _create_folders(self) -> None:
        self.shared.create_folder(path=self.folders[FolderType.MERGED])
        self.shared.create_folder(path=self.folders[FolderType.CLOUD])
        self.shared.create_folder(path=self.folders[FolderType.CLEANED])

    @staticmethod
    def _find_band(band_type: Union[BandType, AddBandType], tile_folder: str) -> str:
        find_band, *_ = [filename for filename in os.listdir(tile_folder) if filename.endswith(band_type)]
        band_path: str = os.path.join(tile_folder, find_band)
        return band_path

    def _match_band(self, band_type: Union[BandType, AddBandType], tile_folder: str):
        if isinstance(band_type, BandType):
            return self._find_band(band_type=band_type, tile_folder=tile_folder)
        elif isinstance(band_type, AddBandType):
            if band_type is AddBandType.SCL:
                return self._find_band(band_type=band_type, tile_folder=tile_folder)
            elif band_type is AddBandType.XML:
                find_xml, *_ = [
                    filename
                    for filename in os.listdir(tile_folder)
                    if filename.startswith("MTD") and filename.endswith(".xml")
                ]
                xml_path: str = os.path.join(tile_folder, find_xml)
                return xml_path
        raise InvalidParameterException()
