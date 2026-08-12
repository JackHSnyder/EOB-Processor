from enum import Enum

class ParseState(Enum):
    SEARCHING = 0
    LAST_NAME = 1
    FIRST_NAME = 2
    DOS = 3


class FileType(Enum):
    MEDICARE = 0
    BLUECROSS = 1