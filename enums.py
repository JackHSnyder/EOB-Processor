from enum import Enum

class FileType(Enum):
    MEDICARE = 0
    BLUECROSS = 1
    ANTHEM = 2

class SettingType(Enum):
    DNE = 0
    SETTING = 1
    EXCEPTION = 2
    DEBUG = 3

class ExceptionType(Enum):
    DNE = 0
    PREFIX = 1
    MIDDLE_INITIAL = 2

class NameExceptionType(Enum):
    MIDDLE_INITIAL = 0
    NO_MIDDLE_INITIAL = 1
    SPELLING = 2