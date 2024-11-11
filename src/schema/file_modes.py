from enum import Enum


class FileMode(str, Enum):
    READ = "r"
    READ_B = "rb"
    WRITE = "w"
    WRITE_B = "wb"
    APPEND = "a"

    def __str__(self) -> str:
        return self.value
