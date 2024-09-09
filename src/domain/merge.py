import os
from typing import Optional, Dict, List, Union, Tuple
from loguru import logger
from os import listdir
from osgeo import gdal
import numpy as np
import rasterio
from rasterio.enums import Resampling


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
                self.folders[FolderType.MERGED],
                f"{index+1}. {date} {tile} {cloud_percentage}%.tiff",
            )
            cloud_10_filename: str = os.path.join(
                self.folders[FolderType.CLOUD],
                f"{index+1}. Cloud {date} {tile} {cloud_percentage}%.tiff",
            )
            cloud_20_filename = os.path.join(
                self.folders[FolderType.CLOUD],
                f"{index+1}. Cloud {date} {tile} {cloud_percentage}%_20m.tiff",
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
                    xRes=20,
                    yRes=20,
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
                self._remove_clouds(
                    scl_10_band=cloud_10_filename,
                    scl_20_band=cloud_20_filename,
                    band=band_path,
                    output_path=output_path,
                )
            logger.info("DONE")

    def _remove_clouds(self, scl_10_band: str, scl_20_band: str, band: str, output_path: str):
        values_to_check: List[int] = [1, 3, 8, 9, 10, 11]

        # Open the high-resolution SCL band (scl_band)
        with rasterio.open(scl_10_band) as second_raster:
            scl_10_band = second_raster.read(1)  # Read the cloud mask from scl_band

            # Open the lower-resolution SCL band (scl_20_band)
            with rasterio.open(scl_20_band) as scl_20_raster:
                scl_20_band_data = scl_20_raster.read(1)  # Read the cloud mask from scl_20_band

            with rasterio.open(band) as first_raster:
                profile = first_raster.profile
                modified_layers = []

                print("BAND", first_raster.shape)
                print("SCL 10:", scl_10_band.shape)
                print("SCL 20:", scl_20_band_data.shape)

                # Check if the high-resolution SCL band matches the first raster shape
                if scl_10_band.shape == first_raster.shape:
                    mask_band = scl_10_band  # Use the high-resolution mask (10980, 10980)
                    logger.info("NAUDOJU BEST")
                else:
                    # If not, check if the lower-resolution SCL band matches the first raster shape
                    if scl_20_band_data.shape == first_raster.shape:
                        mask_band = scl_20_band_data  # Use the lower-resolution mask (5490, 5490)
                        logger.info("NAUDOJU 20")
                    else:
                        logger.info("NESAMONE DARAU")
                        # If neither match, resample the high-res SCL to match the first raster
                        mask_band = second_raster.read(
                            1,
                            out_shape=(first_raster.height, first_raster.width),
                            resampling=Resampling.nearest,  # Resampling method (nearest neighbor in this case)
                        )

                # Iterate through each layer in the first raster
                for i in range(1, first_raster.count + 1):
                    first_band = first_raster.read(i)

                    # Apply the condition: set pixels to 0 where the mask band has values in the list
                    first_band = np.where(np.isin(mask_band, values_to_check), 0, first_band)

                    # Convert to a supported data type (e.g., uint16)
                    if first_band.dtype == "float32":
                        first_band = first_band.astype(np.uint16)

                    # Add the modified band to the list
                    modified_layers.append(first_band)

                # Update the profile to use a supported data type
                profile.update(dtype=rasterio.uint16)

                # Write the modified layers to a new raster file
                with rasterio.open(output_path, "w", **profile) as dst:
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
