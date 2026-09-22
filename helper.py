from difflib import SequenceMatcher

import re
import string
import shutil

from doctr.models import ocr_predictor

import Settings


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


def printDocument(wordArray):
    for word in wordArray:
        print(word, end=" ")


def setupOCR():
    model = ocr_predictor(
        det_arch="db_resnet50",
        reco_arch="crnn_vgg16_bn",
        pretrained=True)
    return model


def findNext(wordArray, target, caseInsensitive = True, punctuationInsensitive = True, spaceInsensitive = True, tolerance = 0):
    if caseInsensitive:
        target = target.upper()

    for i, word in enumerate(wordArray):
        word, separation = cleanWord(word, caseInsensitive, punctuationInsensitive, spaceInsensitive)

        if word == target:
            if separation:
                wordArray.insert(i + 1, separation)

            return i

    # Only bother checking similarity if the search fails the first time and tolerance was given
    if tolerance > 0:
        for i, word in enumerate(wordArray):
            word, separation = cleanWord(word, caseInsensitive, punctuationInsensitive, spaceInsensitive)

            if isSimilar(word, target, tolerance):
                if separation:
                    wordArray.insert(i + 1, separation)

                return i

    return -1  # Target not found

def isSimilar(wordA, wordB, tolerance):
    similarity = SequenceMatcher(None, wordA, wordB).ratio()
    if similarity >= 1 - tolerance:
        return True

    return False

def cleanWord(word, caseInsensitive = True, punctuationInsensitive = True, spaceInsensitive = True):
    separation = ""

    if spaceInsensitive:
        word = word.strip()

    if caseInsensitive:
        word = word.upper()

    # Split word at any punctuation at most once
    if punctuationInsensitive:
        words = splitAt(word, string.punctuation, 1)
        word = words[0] if words else ""
        separation = words[1] if len(words) > 1 else ""

    return word, separation

def splitAt(word, chars, maxsplits=0):
    return [part for part in re.split(f"[{re.escape(chars)}]", word, maxsplit=maxsplits) if part]


def recordService(patients, patient):
    if patient in patients:
        patients[patients.index(patient)].newDOS(patient.startDOS)
        # Debug
        if Settings.debug.get("printPatients"):
            print(patients[patients.index(patient)])

    else:
        patients.append(patient)
        # Debug
        if Settings.debug.get("printPatients"):
            print(patient)


def parseFullName(name):
    firstName = ""
    lastName = ""
    middleInitial = ""
    suffix = ""

    parts = splitAt(name, ",", maxsplits=1)

    if len(parts) > 1:
        firstName = parts[1].strip().lower()
        lastName = parts[0].strip().lower()
    else:
        lastName = parts[0].strip().lower()

    suffixIndex = lastName.rfind(" ")
    if suffixIndex != -1:
        potentialSuffix = lastName[suffixIndex + 1:].strip().lower()
        if isNameSuffix(potentialSuffix):
            suffix = potentialSuffix
            lastName = lastName[:suffixIndex]

    parts = splitAt(firstName, " ")
    for part in parts:
        cleanPart = part.strip().replace(".", "").replace("-", "")
        if len(cleanPart) == 1:
            middleInitial = cleanPart
            firstName = firstName[:firstName.find(part) - 1]
            break
        elif cleanPart.isdigit():
            firstName = firstName[:firstName.find(part) - 1]
            break

    return firstName, lastName, middleInitial, suffix
    

def makeDuplicateFile(original, duplicatePath):
    if not duplicatePath.exists():
        shutil.copy2(original, duplicatePath)
        return

    stem = duplicatePath.stem
    suffix = duplicatePath.suffix
    counter = 1

    while duplicatePath.exists():
        duplicatePath = duplicatePath.with_name(f"{stem} ({counter}){suffix}")
        counter += 1

    shutil.copy2(original, duplicatePath)

def isNameSuffix(word):
    for suffix in nameSuffixes:
        if word.upper() == suffix:
            return True

    return False