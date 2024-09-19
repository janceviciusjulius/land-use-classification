from enum import Enum
from typing import Tuple


class BandType(tuple, Enum):
    B2 = ("B02.jp2", "B02_10m.jp2")
    B3 = ("B03.jp2", "B03_10m.jp2")
    B4 = ("B04.jp2", "B04_10m.jp2")
    B5 = ("B05.jp2", "B05_20m.jp2")
    B6 = ("B06.jp2", "B06_20m.jp2")
    B7 = ("B07.jp2", "B07_20m.jp2")
    B8 = ("B08.jp2", "B08_10m.jp2")
    B8A = ("B08.jp2", "B8A_20m.jp2")
    B11 = ("B11.jp2", "B11_20m.jp2")
    B12 = ("B12.jp2", "B12_20m.jp2")

    def __str__(self) -> Tuple[str, ...]:
        return self.value


class AddBandType(tuple, Enum):
    SCL = ("SCL_20m.jp2",)
    XML = ("MTD", ".xml")

    def __str__(self) -> Tuple[str, ...]:
        return self.value