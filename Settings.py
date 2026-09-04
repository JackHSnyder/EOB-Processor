from enums import ExceptionType

class Settings:
    namePrefixes = []
    initialNames = []
    sendToFolders = False
    foldersDirectory = ""

    def readSettings(settingsPath):
        with open(settingsPath, "r") as file:
            Settings.getExceptions(file)
            Settings.getOtherSettings(file)

    def getExceptions(file):
        exceptionType = ExceptionType.NONE

        for line in file:
            line = line.strip()

            if not line:
                ExceptionType = ExceptionType.NONE
                continue

            match exceptionType:
                case ExceptionType.NONE:
                    if "PREFIXED NAMES" in line.upper():
                        exceptionType = ExceptionType.PREFIX
                        continue

                    elif "INCLUDE MIDDLE INITIAL" in line.upper():
                        exceptionType = ExceptionType.MIDDLE_INITIAL
                        continue

                case ExceptionType.PREFIX:
                    Settings.prefixNames.append(line)

                case ExceptionType.MIDDLE_INITIAL:
                    Settings.initialNames.append(line)

    def getOtherSettings(file):
        for line in file:
            line = line.strip().upper()

            if not line:
                continue

            elif "AUTO SEND TO FOLDERS" in line and "TRUE" in line:
                Settings.sendToFolders = True
                continue

            elif "FOLDERS DIRECTORY" in line:
                Settings.foldersDirectory = line.split(":", 1)[1].strip()
                continue
