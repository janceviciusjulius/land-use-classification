from enum import Enum


class ClassificationType(Enum):
    GROUND = "Ground"
    URBAN = "Urban"
    FOREST = "Forest"

    def __str__(self) -> str:
        return self.value
