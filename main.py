from pathlib import Path
import sys

import helper
from helper import parseState

from Patient import Patient

from Date import Date


def incorrectInputError():
    print("Please drag an EOB in PDF format onto this application.")
    input ("Press 'Enter' to exit...")
    sys.exit(1)


def identifyFilePaths():
    filePath = ""
    exceptionsPath = ""

    for argument in sys.argv[1:]:
        if not filePath and argument[-3:] == "pdf":
            filePath = argument
        elif not exceptionsPath and "exceptions.txt" in argument:
            exceptionsPath = argument

    return filePath, exceptionsPath


def setup(filePath):
    return helper.getWordsFromPDF(helper.setupPDFReader(filePath))


def recordService(patients, patient):
    if patient in patients:
        patients[patients.index(patient)].newDOS(patient.startDOS)
    else:
        patients.append(patient)


def checkExceptions(patients, exceptionsPath):
    exceptions = helper.getExceptions(exceptionsPath)

    for exception in exceptions:
        if exception in patients:
            patients[patients.index(exception)].setException()


def makeDuplicates(patients, filePath):
    original = Path(filePath)

    for patient in patients:
        print(patient)
        duplicate = original.with_name(str(patient) + ".pdf")
        helper.makeDuplicateFile(original, duplicate)


def extractPatients(wordArray):
    patients = []
    tempPatient = Patient()
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
                if word == "MID":
                    state = parseState.DOS

                else:
                    if word.find(".") != -1:
                        first, middle = helper.separateMiddleInitial(word)

                        tempPatient.addToFirstName(first)
                        tempPatient.setMiddleInitial(middle)

                        state = parseState.DOS

                    else:
                        tempPatient.addToFirstName(word)

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

    wordArray = setup(filePath)

    patients = extractPatients(wordArray)

    if exceptionsPath:
        checkExceptions(patients, exceptionsPath)

    makeDuplicates(patients, filePath)

    sys.exit(0)