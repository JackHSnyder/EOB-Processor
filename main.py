from pathlib import Path
import sys

import helper
from enums import FileType
from Medicare import Medicare
from BlueCross import BlueCross
from Patient import Patient
from Settings import Settings

# Debug Variables - All should be false for packaging
printDoc = True
printPatients = True  # Exceptions not accounted for in print

createDuplicates = True


def incorrectInputError():
    print("Please drag an EOB in PDF format onto this application.")
    input ("Press 'Enter' to exit...")
    sys.exit(1)


def identifyFilePaths():
    filePath = ""
    settingsPath = ""

    for argument in sys.argv[1:]:
        if not filePath and argument[-3:].lower() == "pdf":
            filePath = argument
        elif not settingsPath and "settings.txt" in argument.lower():
            settingsPath = argument

    return filePath, settingsPath


def setup(filePath):
    return helper.getWordsFromPDF(helper.setupPDFReader(filePath))


def checkExceptions(patients):
    for patient in patients:
        if patient.getFirstLastName() in Settings.initialNames:
            patient.setException(True)

        correctCapitalization = next((s for s in Settings.prefixNames if s.lower() == patient.getLastName().lower()), None)
        if correctCapitalization:
            patient.setLastName(correctCapitalization)

def makeDuplicates(patients, filePath):
    original = Path(filePath)

    for patient in patients:
        duplicate = original.with_name(str(patient) + ".pdf")
        helper.makeDuplicateFile(original, duplicate)


def findFileType(wordArray):
    for word in wordArray:
        if word == "MEDICARE":
            return FileType.MEDICARE
        elif word == "BlueCross":
            return FileType.BLUECROSS

    return FileType.MEDICARE

def main():
    if len(sys.argv) < 2:
        incorrectInputError()

    filePath, settingsPath = identifyFilePaths()

    if not filePath:
        incorrectInputError()

    if settingsPath:
        Settings.readSettings(settingsPath)


    # Debug
    if printDoc:
        helper.printDocument(helper.setupPDFReader(filePath))


    wordArray = setup(filePath)

    match findFileType(wordArray):
        case FileType.MEDICARE:
            Patient.setMedicare(True)
            patients = Medicare.extractPatients(wordArray)

        case FileType.BLUECROSS:
            Patient.setMedicare(False)
            patients = BlueCross.extractPatients(wordArray)


    if settingsPath:
        checkExceptions(patients)

    if createDuplicates:
        makeDuplicates(patients, filePath)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input ("\nPress Enter to exit...")
    
    sys.exit(0)