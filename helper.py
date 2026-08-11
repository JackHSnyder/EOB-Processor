from doctr.io import DocumentFile
from doctr.models import ocr_predictor

import shutil

from enum import Enum
from Patient import Patient


class parseState(Enum):
    SEARCHING = 0
    LAST_NAME = 1
    FIRST_NAME = 2
    DOS = 3


def splitAtChar(string, char):
    index = string.find(char)
    if index != -1:
        return string[:index], string[index + 1:].strip()
    else:
        return string, ""


def separateMiddleInitial(string):
    index = string.find(".")
    if index != -1:
        string = string[:index]  # Removes period from middle initial and any potential unexpected following strings
        return string[:-1].strip(), string[-1]
    else:
        return string.strip(), ""


def printDocument(pdf):
    for page in pdf.pages:
        for block in page.blocks:
            for line in block.lines:
                print(" ".join(word.value for word in line.words))


def getWordsFromPDF(pdf):
    wordArray = []
    
    for page in pdf.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    wordArray.append(word.value)

    return wordArray


def setupPDFReader(filePath):
    model = ocr_predictor(
        det_arch="db_resnet50",
        reco_arch="crnn_vgg16_bn",
        pretrained=True)
    doc = DocumentFile.from_pdf(filePath)
    pdf = model(doc)

    return pdf


def getExceptions(exceptionsPath):
    exceptions = []

    tempException = Patient()

    with open(exceptionsPath, "r") as file:
        for line in file:
            lastName, rest = splitAtChar(line, ",")

            if lastName:
                firstName, middleInitial = separateMiddleInitial(rest)

                tempException.lastName = lastName
                tempException.firstName = firstName
                tempException.middleInitial = middleInitial

                exceptions.append(tempException)
                tempException = Patient()

    return exceptions


def makeDuplicateFile(original, duplicate):
    if not duplicate.exists():
        shutil.copy2(original, duplicate)
        return

    stem = duplicate.stem
    suffix = duplicate.suffix
    counter = 1

    while duplicate.exists():
        duplicate = original.with_name(f"{stem} ({counter}){suffix}")
        counter += 1

    shutil.copy2(original, duplicate)