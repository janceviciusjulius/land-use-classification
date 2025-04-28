from enum import Enum


class ReadType(str, Enum):
    UINT8 = "uint8"
    FLOAT32 = "float32"

    def __str__(self) -> str:
        return self.value
