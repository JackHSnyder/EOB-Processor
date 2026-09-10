from pathlib import Path
import sys

import helper
import Settings
from enums import FileType
from Medicare import Medicare
from BlueCross import BlueCross
from Anthem import Anthem
from Patient import Patient
from DocumentHandler import DocumentHandler

def incorrectInputError():
    print("Please drag an EOB in PDF format onto this application.")
    input ("Press 'Enter' to exit...")
    sys.exit(1)


def identifyFilePaths():
    filePaths = []
    settingsPath = ""

    for argument in sys.argv[1:]:
        if argument[-3:].lower() == "pdf":
            filePaths.append(argument)
        elif not settingsPath and "settings.txt" in argument.lower():
            settingsPath = argument

    return filePaths, settingsPath


def makeDuplicates(patients, filePath):
    original = Path(filePath)

    for patient in patients:
        duplicate = original.with_name(str(patient) + ".pdf")
        helper.makeDuplicateFile(original, duplicate)


def getFileType():
    print("What type of EOBs were given?")
    print("1. Medicare     2. BlueCross     3. Anthem")

    while(True):
        type = input("Answer as one of the above numbers: ")

        if type == "1":
            return FileType.MEDICARE
        elif type == "2":
            return FileType.BLUECROSS
        elif type == "3":
            return FileType.ANTHEM

def main():
    if len(sys.argv) < 2:
        incorrectInputError()

    filePaths, settingsPath = identifyFilePaths()

    if len(filePaths) == 0:
        incorrectInputError()

    if settingsPath:
        Settings.readSettings(settingsPath)

    fileType = getFileType()

    for filePath in filePaths:
        wordArray = DocumentHandler.getWordsFromPDF(fileType, filePath)

        # Debug
        if Settings.debug.get("printDoc"):
            helper.printDocument(wordArray)

        match fileType:
            case FileType.MEDICARE:
                Patient.setMedicare()
                patients = Medicare.extractPatients(wordArray)

            case FileType.BLUECROSS:
                patients = BlueCross.extractPatients(wordArray)

            case FileType.ANTHEM:
                patients = Anthem.extractPatients(wordArray)

        if settingsPath:
            Settings.checkExceptions(patients)

        if Settings.createDuplicates:
            makeDuplicates(patients, filePath)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input ("\nPress Enter to exit...")
    
    sys.exit(0)