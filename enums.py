from enum import Enum

class ParseState(Enum):
    SEARCHING = 0
    NAME = 1
    DOS = 2


class FileType(Enum):
    MEDICARE = 0
    BLUECROSS = 1