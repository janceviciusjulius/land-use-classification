from enum import Enum


class YesNo(str, Enum):
    YES = "y"
    NO = "n"

    def __str__(self) -> str:
        return self.value
