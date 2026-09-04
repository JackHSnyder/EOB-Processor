from doctr.io import DocumentFile
from doctr.models import ocr_predictor

import shutil

from Patient import Patient

# Debug variable
from main import printPatients


nameSuffixes = ["JR", "SR", "II", "III", "IV", "V", "VI"]

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

def isNameSuffix(word):
    for suffix in nameSuffixes:
        if word.upper() == suffix:
            return True

    return False