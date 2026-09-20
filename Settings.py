import string
from pathlib import Path

from enums import ExceptionType
from enums import SettingType

import helper

namePrefixes = []
initialNames = []
sendToFolders = False
foldersDirectory = ""
createDuplicates = True
debug = {}

def readSettings(settingsPath):
    with open(settingsPath, "r") as file:
        settingType = SettingType.DNE
        exceptionType = ExceptionType.DNE

        for line in file:
            line = line.strip()

            if not line:
                continue

            if line == "~ SETTINGS ~":
                settingType = SettingType.SETTING
                continue
            elif line == "~ EXCEPTIONS ~":
                settingType = SettingType.EXCEPTION
                continue
            elif line == "~ DEBUG ~":
                settingType = SettingType.DEBUG
                continue

            match settingType:
                case SettingType.SETTING:
                    getSettings(line)
                case SettingType.EXCEPTION:
                    exceptionType = getExceptions(line, exceptionType)
                case SettingType.DEBUG:
                    getDebugSettings(line)

def getSettings(line):
    global sendToFolders
    global foldersDirectory
    global createDuplicates

    line = line.upper()

    if "AUTO SEND TO FOLDERS" in line and "TRUE" in line:
        sendToFolders = True

    elif "FOLDERS DIRECTORY" in line:
        foldersDirectory = line.split(":", 1)[1].strip()

    elif "CREATEDUPLICATES" in line and "FALSE" in line:
        createDuplicates = False

def getExceptions(line, exceptionType):
    lineUpper = line.upper()
    if "PREFIXED NAMES" in lineUpper:
        return ExceptionType.PREFIX
    elif "INCLUDE MIDDLE INITIAL" in lineUpper:
        return ExceptionType.MIDDLE_INITIAL

    match exceptionType:
        case ExceptionType.PREFIX:
            namePrefixes.append(line)
            return ExceptionType.PREFIX

        case ExceptionType.MIDDLE_INITIAL:
            initialNames.append(line)
            return ExceptionType.MIDDLE_INITIAL

def getDebugSettings(line):
    if not "=" in line:
        return
    
    key, value = line.split("=", 1)

    value = value.strip().upper()
    if value == "TRUE":
        value = True
    elif value == "FALSE":
        value = False

    debug[key.strip()] = value


def checkExceptions(patients):
    for patient in patients:
        for name in initialNames:
            fn, ln, mi, s = helper.parseFullName(name)

            if fn == patient.getFirstName().lower() and ln == patient.getLastName().lower():
                patient.setException()
    
        # Ignores capitalization and punctuation for the check, but stores the correct format if passed
        cleanedPatient, pt2 = helper.cleanWord(patient.getLastName())
        cleanedPatient = cleanedPatient + pt2
        for name in namePrefixes:
            cleanedName, pt2 = helper.cleanWord(name)
            cleanedName = cleanedName + pt2

            if cleanedPatient == cleanedName:
                patient.setLastName(name)
                break


def getPatientFolders():
    path = Path(foldersDirectory)

    if sendToFolders and path.is_dir():
        return [f for f in path.iterdir() if f.is_dir()]
    else:
        return []