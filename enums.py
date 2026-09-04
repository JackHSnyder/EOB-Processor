from enum import Enum

class ParseState(Enum):
    SEARCHING = 0
    NAME = 1
    DOS = 2


class FileType(Enum):
    MEDICARE = 0
    BLUECROSS = 1


class ExceptionType(Enum):
    NONE = 0
    PREFIX = 1
    MIDDLE_INITIAL = 2