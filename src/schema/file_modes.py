from enum import Enum


class FileMode(str, Enum):
    READ = "r"
    WRITE = "w"
    APPEND = "a"

    def __str__(self) -> str:
        return self.value
