from pathlib import Path
import sys

import helper
from enums import FileType
from Medicare import Medicare
from BlueCross import BlueCross
from Patient import Patient

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
    exceptionsPath = ""

    for argument in sys.argv[1:]:
        if not filePath and argument[-3:].lower() == "pdf":
            filePath = argument
        elif not exceptionsPath and "exceptions.txt" in argument.lower():
            exceptionsPath = argument

    return filePath, exceptionsPath


def setup(filePath):
    return helper.getWordsFromPDF(helper.setupPDFReader(filePath))


def checkExceptions(patients, exceptionsPath):
    exceptions = helper.getExceptions(exceptionsPath)

    for exception in exceptions:
        if exception in patients:
            patients[patients.index(exception)].setException()


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        incorrectInputError()

    filePath, exceptionsPath = identifyFilePaths()

    if not filePath:
        incorrectInputError()

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

    if exceptionsPath:
        checkExceptions(patients, exceptionsPath)

    if createDuplicates:
        makeDuplicates(patients, filePath)

    sys.exit(0)