import json
from enum import Enum
from typing import Dict, Any


# Define the Enum
class FolderType(Enum):
    PARENT = "PARENT"
    DOWNLOAD = "DOWNLOAD"
    ZIP = "ZIP"
    MOVED = "MOVED"
    MERGED = "MERGED"
    CLEANED = "CLEANED"
    CLOUD = "CLOUD"
    JOINED = "JOINED"
    CLASSIFIED = "CLASSIFIED"


# Example JSON data (as a string for demonstration purposes)
json_data = """
{
    "interpolation": true,
    "start_date": "2024-09-01",
    "end_date": "2024-09-04",
    "max_cloud_cover": 0,
    "folders": {
        "PARENT": "/path/to/parent",
        "DOWNLOAD": "/path/to/download",
        "ZIP": "/path/to/zip",
        "MOVED": "/path/to/moved",
        "MERGED": "/path/to/merged",
        "CLEANED": "/path/to/cleaned",
        "CLOUD": "/path/to/cloud",
        "JOINED": "/path/to/joined",
        "CLASSIFIED": "/path/to/classified"
    }
}
"""


def load_json_with_enum(json_str: str, enum_type: Enum) -> Dict[str, Any]:
    data = json.loads(json_str)

    if "folders" in data:
        data["folders"] = {enum_type[key]: value for key, value in data["folders"].items()}

    return data


# Load the JSON data
loaded_data = load_json_with_enum(json_data, FolderType)

# Example usage
print(loaded_data)
print(type(loaded_data["folders"][FolderType.PARENT]))  # Should be <class 'str'>, showing values
