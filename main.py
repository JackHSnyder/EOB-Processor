from pathlib import Path
import string
import sys

from doctr.io import DocumentFile

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
        # Ignores capitalization
        if any(s.lower() == patient.getFirstLastName().lower() for s in Settings.initialNames):
            patient.setException()

        # Ignores capitalization and punctuation for the check, but stores the correct format if passed
        correctForm = next((s for s in Settings.namePrefixes if s.lower() == patient.getLastName().lower() or s.lower().translate(str.maketrans('', '', string.punctuation)) == patient.getLastName().lower()), None)
        if correctForm:
            patient.setLastName(correctForm)

def makeDuplicates(patients, filePath):
    original = Path(filePath)

    for patient in patients:
        duplicate = original.with_name(str(patient) + ".pdf")
        helper.makeDuplicateFile(original, duplicate)

def getWordsFromPDF(fileType, filePath):
    doc = DocumentFile.from_pdf(filePath)

    if fileType == FileType.MEDICARE:
        doc = Medicare.shapeDocument(doc)
    elif fileType == FileType.BLUECROSS:
        doc = BlueCross.shapeDocument(doc)
    else:
        raise ValueError("Not equipped to handle this file type.")

    model = helper.setupOCR()
    pdf = model(doc)

    wordArray = []

    for page in pdf.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    wordArray.append(word.value)
                wordArray.append("\n")
                
    return wordArray

def getFileType():
    print("What type of EOBs were given?")
    print("1. Medicare     2. BlueCross")

    while(True):
        type = input("Answer as one of the above numbers: ")

        if type == "1":
            return FileType.MEDICARE
        elif type == "2":
            return FileType.BLUECROSS

def main():
    if len(sys.argv) < 2:
        incorrectInputError()

    filePath, settingsPath = identifyFilePaths()

    if not filePath:
        incorrectInputError()

    if settingsPath:
        Settings.readSettings(settingsPath)

    fileType = getFileType()

    wordArray = getWordsFromPDF(fileType, filePath)

    # Debug
    if printDoc:
        helper.printDocument(wordArray)

    match fileType:
        case FileType.MEDICARE:
            Patient.setMedicare()
            patients = Medicare.extractPatients(wordArray)

        case FileType.BLUECROSS:
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