from enum import Enum

class FileType(Enum):
    MEDICARE = 0
    BLUECROSS = 1

class ExceptionType(Enum):
    DNE = 0
    PREFIX = 1
    MIDDLE_INITIAL = 2