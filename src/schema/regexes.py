from enum import Enum


class Regex(str, Enum):
    DATE_REGEX1 = r"(\d{4})(\d{2})(\d{2})"
    DATE_REGEX2 = r"(\d{4})-(\d{2})-(\d{2})"
