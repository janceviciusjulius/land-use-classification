from time import perf_counter
from typing import Any, Dict, List

from domain.merge import Merge
from domain.shared import Shared
from schema.metadata_types import CloudCoverageJson
from schema.tile_types import TileType

cloud_data_path: str = (
    "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-04 0-0%/information.json"
)
images_data: Dict[str, Dict[str, Any]] = {
    "S2A_MSIL2A_20240901T100031_N0511_R122_T34UDG_20240901T152251.SAFE": {
        "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34UDG_20240901T152251.SAFE",
        "cloud": 10.0,
        "date": "20240901",
        "tile": "T34UDG",
        "filename": "/path/to/file/2024-09-01_T34UDG_0.0%.tiff",
    },
    "S2A_MSIL2A_20240902T100031_N0511_R122_T34UDG_20240902T152252.SAFE": {
        "title": "S2A_MSIL2A_20240902T100031_N0511_R122_T34UDG_20240902T152252.SAFE",
        "cloud": 5.0,
        "date": "20240902",
        "tile": "T34UDG",
        "filename": "/path/to/file/2024-09-02_T34UDG_5.0%.tiff",
    },
    "S2A_MSIL2A_20240901T100031_N0511_R122_T34VDH_20240901T152253.SAFE": {
        "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34VDH_20240901T152253.SAFE",
        "cloud": 22.0,
        "date": "20240901",
        "tile": "T34VDH",
        "filename": "/path/to/file/2024-09-01_T34VDH_2.0%.tiff",
    },
    "S2A_MSIL2A_20240902T100031_N0511_R122_T34VDH_20240902T152254.SAFE": {
        "title": "S2A_MSIL2A_20240902T100031_N0511_R122_T34VDH_20240902T152254.SAFE",
        "cloud": 7.0,
        "date": "20240902",
        "tile": "T34VDH",
        "filename": "/path/to/file/2024-09-02_T34VDH_7.0%.tiff",
    },
}

match_images: Dict[TileType, List[Dict[str, Any]]] = Merge.match_images_with_tiles(images_data=images_data)
sorted_data: Dict[TileType, List[Dict[str, Any]]] = Merge.sort_image_info(
    criteria=CloudCoverageJson.CLOUD, match_images=match_images
)

print(match_images)
print(sorted_data)


# print()
# for match, sorts in zip(match_images, sorted_data):
#     print(match_images)
#     print(sorted_data)
#     print()

# for data in match_images.values():
#     print(data)
#     sorted_data =  sorted(data, key=lambda x: x['cloud'])
#
#     print(data)
#     print("KITAS TILE")

x = {
    "T34UDG": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34UDG_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34UDG",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/7. 20240901 T34UDG 0.0%.tiff",
        }
    ],
    "T34VDH": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34VDH_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34VDH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/6. 20240901 T34VDH 0.0%.tiff",
        }
    ],
    "T34VEH": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34VEH_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34VEH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/2. 20240901 T34VEH 0.0%.tiff",
        }
    ],
    "T34UEG": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34UEG_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34UEG",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/3. 20240901 T34UEG 0.0%.tiff",
        }
    ],
    "T34VFH": [
        {
            "title": "S2B_MSIL2A_20240907T093039_N0511_R136_T34VFH_20240907T121433.SAFE",
            "cloud": 0.0,
            "date": "20240907",
            "tile": "T34VFH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/4. 20240907 T34VFH 0.0%.tiff",
        }
    ],
    "T34UFG": [],
    "T34UFF": [],
    "T34UFE": [],
    "T34UGE": [],
    "T34UEF": [],
    "T35VLC": [],
    "T35ULB": [
        {
            "title": "S2A_MSIL2A_20240908T095031_N0511_R079_T35ULB_20240908T131845.SAFE",
            "cloud": 0.0,
            "date": "20240908",
            "tile": "T35ULB",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/1. 20240908 T35ULB 0.0%.tiff",
        }
    ],
    "T35ULA": [],
    "T35ULV": [],
    "T35VMC": [],
    "T35UMB": [],
    "T35UMA": [],
}
y = {
    "T34UDG": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34UDG_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34UDG",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/7. 20240901 T34UDG 0.0%.tiff",
        }
    ],
    "T34VDH": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34VDH_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34VDH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/6. 20240901 T34VDH 0.0%.tiff",
        }
    ],
    "T34VEH": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34VEH_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34VEH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/2. 20240901 T34VEH 0.0%.tiff",
        }
    ],
    "T34UEG": [
        {
            "title": "S2A_MSIL2A_20240901T100031_N0511_R122_T34UEG_20240901T152250.SAFE",
            "cloud": 0.0,
            "date": "20240901",
            "tile": "T34UEG",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/3. 20240901 T34UEG 0.0%.tiff",
        }
    ],
    "T34VFH": [
        {
            "title": "S2B_MSIL2A_20240907T093039_N0511_R136_T34VFH_20240907T121433.SAFE",
            "cloud": 0.0,
            "date": "20240907",
            "tile": "T34VFH",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/4. 20240907 T34VFH 0.0%.tiff",
        }
    ],
    "T34UFG": [],
    "T34UFF": [],
    "T34UFE": [],
    "T34UGE": [],
    "T34UEF": [],
    "T35VLC": [],
    "T35ULB": [
        {
            "title": "S2A_MSIL2A_20240908T095031_N0511_R079_T35ULB_20240908T131845.SAFE",
            "cloud": 0.0,
            "date": "20240908",
            "tile": "T35ULB",
            "filename": "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-11 0-0%/CLEANED 2024-09-01..2024-09-11 0-0%/1. 20240908 T35ULB 0.0%.tiff",
        }
    ],
    "T35ULA": [],
    "T35ULV": [],
    "T35VMC": [],
    "T35UMB": [],
    "T35UMA": [],
}
