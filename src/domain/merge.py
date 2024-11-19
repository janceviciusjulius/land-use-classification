import os
import subprocess
from os import listdir
from typing import Any, Dict, List, Optional, Tuple, Union

import rasterio
from bs4 import BeautifulSoup
from loguru import logger
from numpy import around, isin, nan_to_num, ndarray, seterr, where
from osgeo import gdal
from osgeo.gdal import Band, Dataset
from rasterio.enums import Resampling

from domain.shared import Shared
from exceptions.exceptions import InvalidParameterException
from schema.band_types import AddBandType, BandType
from schema.file_modes import FileMode
from schema.file_types import FileType
from schema.folder_types import FolderType
from schema.formats import Format
from schema.metadata_types import CloudCoverageJson, Metadata
from schema.reading_types import ReadingType
from schema.tile_types import TileType


class Merge:
    GDAL_MERGE: str = "gdal_merge.py"
    XML_PARSER: str = "lxml-xml"
    XML_OFFSET: str = "BOA_ADD_OFFSET"
    BAND_NAMES: Dict[int, str] = {
        1: "Band_4",
        2: "Band_3",
        3: "Band_2",
        4: "Band_5",
        5: "Band_6",
        6: "Band_7",
        7: "Band_8",
        8: "Band_8A",
        9: "Band_11",
        10: "Band_12",
        11: "NDTI",
        12: "NDVIre",
        13: "MNDWI",
    }

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

    def process_data(self) -> None:
        logger.info("Starting merging...")
        self._create_folders()
        self._merge()
        self._set_band_names()
        self._cleaning_data()
        self._cloud_interpolation()
        self._count_indexes()
        self.shared.delete_folder(self.folders[FolderType.MERGED])

    def _count_indexes(self):
        logger.info("Starting index counting process.")
        files: List[str] = os.listdir(self.folders[FolderType.CLEANED])
        for index, file in enumerate(files):
            raster: Optional[Dataset] = gdal.Open(os.path.join(self.folders[FolderType.CLEANED], file), 1)
            band3: Optional[ndarray] = raster.GetRasterBand(2).ReadAsArray()
            band4: Optional[ndarray] = raster.GetRasterBand(1).ReadAsArray()
            band5: Optional[ndarray] = raster.GetRasterBand(4).ReadAsArray()
            band11: Optional[ndarray] = raster.GetRasterBand(9).ReadAsArray()
            band12: Optional[ndarray] = raster.GetRasterBand(10).ReadAsArray()

            write_NDTI: Band = raster.GetRasterBand(11)
            write_NDVIre: Band = raster.GetRasterBand(12)
            write_MNDWI: Band = raster.GetRasterBand(13)
            seterr(invalid="ignore")

            NDTI: Optional[ndarray] = (band11 - band12) / (band11 + band12)
            NDTI: Optional[ndarray] = nan_to_num(NDTI)
            NDTI: Optional[ndarray] = around(NDTI, decimals=4)
            NDTI: Optional[ndarray] = NDTI * 10000
            NDTI: Optional[ndarray] = NDTI.astype(ReadingType.INT16)
            write_NDTI.WriteArray(NDTI)

            NDVIre: Optional[ndarray] = (band5 - band4) / (band5 + band4)
            NDVIre: Optional[ndarray] = nan_to_num(NDVIre)
            NDVIre: Optional[ndarray] = around(NDVIre, decimals=4)
            NDVIre: Optional[ndarray] = NDVIre * 10000
            NDVIre: Optional[ndarray] = NDVIre.astype(ReadingType.INT16)
            write_NDVIre.WriteArray(NDVIre)

            MNDWI: Optional[ndarray] = (band3 - band11) / (band3 + band11)
            MNDWI: Optional[ndarray] = nan_to_num(MNDWI)
            MNDWI: Optional[ndarray] = around(MNDWI, decimals=4)
            MNDWI: Optional[ndarray] = MNDWI * 10000
            MNDWI: Optional[ndarray] = MNDWI.astype(ReadingType.INT16)
            write_MNDWI.WriteArray(MNDWI)

            raster, band3, band4, band5, band11, band12 = (
                None,
                None,
                None,
                None,
                None,
                None,
            )
            logger.info(f"Successfully counted indexes for {index + 1} file")
        logger.info("End of index counting process")

    def _cloud_interpolation(self) -> None:
        if self.interpolation:
            cloud_data_path: str = self.files[Metadata.CLOUD_COVERAGE]
            images_data: Dict[str, Dict[str, Any]] = self.shared.read_json(path=cloud_data_path)

            match_images: Dict[TileType, List[Dict[str, Any]]] = self.match_images_with_tiles(images_data=images_data)
            sorted_data: Dict[TileType, List[Dict[str, Any]]] = self.sort_image_info(
                criteria=CloudCoverageJson.CLOUD, match_images=match_images
            )

            for image_details in sorted_data.values():
                if len(image_details) > 0:
                    if len(image_details) > 1:
                        for index, details in enumerate(image_details[1:]):
                            best_raster: Optional[Dataset] = gdal.Open(image_details[0][CloudCoverageJson.FILENAME], 1)
                            best_raster_array: Any = best_raster.ReadAsArray().astype(ReadingType.INT16)
                            mask = best_raster_array == 0
                            if mask.all():
                                break
                            interpolation_raster: Optional[Dataset] = gdal.Open(details[CloudCoverageJson.FILENAME], 1)
                            interpolation_raster_array: Optional[ndarray] = interpolation_raster.ReadAsArray().astype(
                                ReadingType.INT16
                            )

                            best_raster_array[mask] = interpolation_raster_array[mask]
                            best_raster.WriteArray(best_raster_array)

                            best_raster, best_raster_array = None, None
                            interpolation_raster, interpolation_raster_array = (
                                None,
                                None,
                            )
                    self._rename_interpolated_filename(
                        filename=image_details[0][CloudCoverageJson.FILENAME],
                        tile=image_details[0][CloudCoverageJson.TILE],
                        interval=image_details[0][CloudCoverageJson.INTERVAL],
                    )
            logger.info("Cloud interpolation process completed successfully.")
        else:
            logger.info(f"Cloud interpolation is skipped.")
        return

    @staticmethod
    def _rename_interpolated_filename(filename: str, tile: str, interval: str) -> None:
        if filename:
            new_filename: str = f"{interval} {tile}{FileType.TIFF.value}"
            new_filename_path = os.path.join(os.path.dirname(filename), new_filename)
            os.rename(filename, new_filename_path)

    @staticmethod
    def sort_image_info(
        criteria: Any, match_images: Dict[TileType, List[Dict[str, Any]]]
    ) -> Dict[TileType, List[Dict[str, Any]]]:
        return {tile: sorted(entries, key=lambda x: x[criteria]) for tile, entries in match_images.items()}

    @staticmethod
    def match_images_with_tiles(images_data: Dict[str, Dict[str, Any]]) -> Dict[TileType, List[Dict[str, Any]]]:
        match_images: Dict[TileType, List[Dict[str, Any]]] = {tile_type.value: [] for tile_type in TileType}
        for tile in TileType:
            for image_data in images_data.values():
                tile_code: str = image_data[CloudCoverageJson.TILE]
                if tile_code == tile.value:
                    match_images[TileType(tile)].append(image_data)
        return match_images

    def _cleaning_data(self):
        logger.info(f"Start of images cleaning processing ...")
        files: List[str] = os.listdir(self.folders[FolderType.MERGED])
        input_file_paths: List[str] = [os.path.join(self.folders[FolderType.MERGED], file) for file in files]
        output_file_paths: List[str] = [os.path.join(self.folders[FolderType.CLEANED], file) for file in files]

        for index, (input_file_path, output_file_path) in enumerate(zip(input_file_paths, output_file_paths)):
            self._clean_warp(input_file_path=input_file_path, output_file_path=output_file_path)
            logger.info(f"Processed {index + 1} file")
        logger.info(f"End of images cleaning processing.")
        self.shared.update_information(
            folder=self.folders[FolderType.CLEANED],
            json_file_path=self.files[Metadata.CLOUD_COVERAGE],
        )

    def _set_band_names(self):
        files: List[str] = os.listdir(self.folders[FolderType.MERGED])
        file_paths: List[str] = [os.path.join(self.folders[FolderType.MERGED], file) for file in files]
        logger.info("Setting band names...")
        for file_path in file_paths:
            raster: Any = gdal.Open(file_path, 1)
            number_of_bands: int = raster.RasterCount
            for band_number in range(number_of_bands):
                band: Band = raster.GetRasterBand(band_number + 1)
                band.SetDescription(self.BAND_NAMES[band_number + 1])
            raster = None
        logger.info("Successfully set band names.")

    def _merge(self) -> None:
        files_information: Dict[str, float] = self.shared.read_json(path=self.files[Metadata.CLOUD_COVERAGE])
        files: List[str] = listdir(self.folders[FolderType.DOWNLOAD])
        logger.info(f"Merge process of the selected folder starts. Folders to merge: {len(files)}")

        for index, file in enumerate(files):
            merge_command: List[str] = []
            temp_working_dir_name: str = os.path.join(self.folders[FolderType.DOWNLOAD], file)
            self.shared.delete_all_xml(temp_working_dir_name)

            cloud_percentage: float = files_information[file][CloudCoverageJson.CLOUD]
            date: str = files_information[file][CloudCoverageJson.DATE]
            tile: str = files_information[file][CloudCoverageJson.TILE]

            out_filename: str = os.path.join(
                self.folders[FolderType.MERGED],
                f"{index+1}. {date} {tile} {cloud_percentage}%{FileType.TIFF.value}",
            )
            cloud_10_filename: str = os.path.join(
                self.folders[FolderType.CLOUD],
                f"{index+1}. Cloud {date} {tile} {cloud_percentage}%{FileType.TIFF.value}",
            )
            cloud_20_filename = os.path.join(
                self.folders[FolderType.CLOUD],
                f"{index+1}. Cloud {date} {tile} {cloud_percentage}%_20m{FileType.TIFF.value}",
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

            self._cloud_warp(dest=cloud_10_filename, src=scl, res=10)
            self._cloud_warp(dest=cloud_20_filename, src=scl, res=20)

            logger.info(f"Successfully prepared {index+1} file cloud files.")
            band_list: Tuple[str, ...] = (b4, b3, b2, b5, b6, b7, b8, b8a, b11, b12)

            processed_bands: List[str] = []
            for band_path in band_list:
                file_name: str = os.path.basename(band_path).replace(FileType.JP2.value, FileType.TIFF.value)
                output_path: str = os.path.join(temp_working_dir_name, f"Processed {file_name}")
                self._remove_clouds(
                    scl_10_band=cloud_10_filename,
                    scl_20_band=cloud_20_filename,
                    band=band_path,
                    output_path=output_path,
                )
                processed_bands.append(output_path)

            parameters: List[str] = [
                self.GDAL_MERGE,
                "-n",
                "0",
                "-a_nodata",
                "0",
                "-separate",
                "-o",
                out_filename,
            ]
            veg_index_bands: List[str] = [processed_bands[0]] * 3

            merge_command.extend(parameters)
            merge_command.extend(processed_bands)
            merge_command.extend(veg_index_bands)

            subprocess.run(merge_command, check=True)
            logger.info(f"Successfully merged {index+1} file.")

            with open(xml, FileMode.READ) as xml_file:
                data = xml_file.read()

            bs_data: BeautifulSoup = BeautifulSoup(data, self.XML_PARSER)
            offset: List[BeautifulSoup] = bs_data.find_all(self.XML_OFFSET)
            offset_values = [element.text for element in offset]
            if all(offset_values) and len(offset_values) > 0:
                offset_value: int = int(offset_values[0])
                raster: Optional[Dataset] = gdal.Open(out_filename, 1)
                raster_array: Optional[ndarray] = raster.ReadAsArray()
                raster_array: Optional[ndarray] = raster_array + offset_value
                raster_array[raster_array < 0] = 0
                raster.WriteArray(raster_array)
                logger.info(f"Successfully changed {index+1} file pixel values.")
                raster, raster_array = None, None
        self.shared.delete_folder(path=self.folders[FolderType.DOWNLOAD])
        logger.info("End of merging process")

    def _cloud_warp(self, dest: str, src: str, res: int) -> None:
        gdal.Warp(
            destNameOrDestDS=dest,
            srcDSOrSrcDSTab=src,
            format=Format.GTIFF,
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
                xRes=res,
                yRes=res,
                callback=self.shared.progress_cb,
                callback_data=".",
            ),
        )

    def _clean_warp(self, input_file_path: str, output_file_path: str) -> None:
        gdal.Warp(
            output_file_path,
            input_file_path,
            format=Format.GTIFF,
            options=gdal.WarpOptions(
                creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"],
                cropToCutline=True,
                dstNodata=0,
                callback=self.shared.progress_cb,
                callback_data=".",
            ),
        )

    @staticmethod
    def _remove_clouds(scl_10_band: str, scl_20_band: str, band: str, output_path: str):
        values_to_check: List[int] = [1, 3, 8, 9, 10, 11]

        with rasterio.open(scl_10_band) as second_raster:
            scl_10_band = second_raster.read(1)

            with rasterio.open(scl_20_band) as scl_20_raster:
                scl_20_band_data = scl_20_raster.read(1)

            with rasterio.open(band) as first_raster:
                profile = first_raster.profile
                modified_layers = []

                if scl_10_band.shape == first_raster.shape:
                    mask_band = scl_10_band
                else:
                    if scl_20_band_data.shape == first_raster.shape:
                        mask_band = scl_20_band_data
                    else:
                        mask_band = second_raster.read(
                            1,
                            out_shape=(first_raster.height, first_raster.width),
                            resampling=Resampling.nearest,
                        )

                for index in range(1, first_raster.count + 1):
                    first_band = first_raster.read(index)

                    first_band = where(isin(mask_band, values_to_check), 0, first_band)
                    first_band[first_band == 1] = 0

                    modified_layers.append(first_band)

                profile.update(dtype=rasterio.int16)

                with rasterio.open(output_path, FileMode.WRITE, **profile) as dst:
                    for idx, layer in enumerate(modified_layers, 1):
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
                    if filename.startswith(FileType.MTD) and filename.endswith(FileType.XML)
                ]
                xml_path: str = os.path.join(tile_folder, find_xml)
                return xml_path
        raise InvalidParameterException()
