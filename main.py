from pathlib import Path
import sys
import string

import helper
from helper import parseState

from Patient import Patient

from Date import Date

# Debug Variables - All should be false for packaging
printDoc = False
printPatients = False  # Exceptions not accounted for in print

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


def recordService(patients, patient):
    if patient in patients:
        patients[patients.index(patient)].newDOS(patient.startDOS)

        # Debug
        if printPatients:
            print(patients[patients.index(patient)])

    else:
        patients.append(patient)

        # Debug
        if printPatients:
            print(patient)


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


def extractPatients(wordArray):
    patients = []
    tempPatient = Patient()
    lastFirstName = ""
    potentialDate = ""
    state = parseState.SEARCHING

    for word in wordArray:
        match state:
            case parseState.SEARCHING:
                if word == "NAME":
                    state = parseState.LAST_NAME

                elif word == "MEDICARE":
                    Patient.setMedicare()

                continue

            case parseState.LAST_NAME:
                if word.find(",") == -1:
                    tempPatient.addToLastName(word)

                else:
                    ln, fn = helper.splitAtChar(word, ",")  # "fn" is blank if the names were correctly spaced
                    tempPatient.addToLastName(ln)
                    tempPatient.addToFirstName(fn)

                    state = parseState.FIRST_NAME

                continue

            case parseState.FIRST_NAME:
                word = word.translate(str.maketrans("", "", string.punctuation))  # Removes any punctuation from the current word - OCR sometimes registers below line as extra "." or "_"

                if not lastFirstName:
                    lastFirstName = word

                elif word == "MID":
                    if len(lastFirstName) == 1:
                        tempPatient.setMiddleInitial(lastFirstName)
                    else:
                        tempPatient.addToFirstName(lastFirstName)

                    state = parseState.DOS

                else:
                    tempPatient.addToFirstName(lastFirstName)
                    lastFirstName = word

                continue

            case parseState.DOS:
                # Dates are always MMDD followed by MMDDYY in the following word
                if potentialDate != "":
                    if word[:4] == potentialDate and len(word) == 6 and word.isdigit():
                        potentialDate = ""
                        tempPatient.newDOS(Date(int(word[:2]), int(word[2:4]), int(word[4:])))

                        state = parseState.SEARCHING
                        recordService(patients, tempPatient)
                        tempPatient = Patient()
                        lastFirstName = ""

                    else:
                        potentialDate = ""

                if len(word) == 4 and word.isdigit():
                    potentialDate = word

                continue

    return patients


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

    patients = extractPatients(wordArray)

    if exceptionsPath:
        checkExceptions(patients, exceptionsPath)

    if createDuplicates:
        makeDuplicates(patients, filePath)

    sys.exit(0)