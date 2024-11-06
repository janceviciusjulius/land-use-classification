from enum import Enum


class Regex(str, Enum):
    DATE_REGEX = r"(\d{4})(\d{2})(\d{2})"
