from difflib import SequenceMatcher
from typing import TypeAlias
from pathlib import Path
import re
import string
import shutil

from doctr.models import ocr_predictor

import Settings
from enums import NameExceptionType


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


def findDirectory(patientFolders, patient):
    directory = ""
    similarityFound = False

    # Creates a list of tuples which are required to have the type NameExceptionType and then str
    exceptions: dict[NameExceptionType, list[Path]] = {
        NameExceptionType.NO_MIDDLE_INITIAL: [],
        NameExceptionType.MIDDLE_INITIAL: [],
        NameExceptionType.SPELLING: []
    }

    for folder in patientFolders:
        folderFirst, folderLast, folderMiddle, _suffix_ = parseFullName(str(folder.name))
        if patient.getFirstName().lower() == folderFirst and patient.getLastName().lower() == folderLast:
            if folderMiddle:
                if patient.middleInitial:
                    if patient.middleInitial == folderMiddle:
                        directory = folder
                        break
                    else:
                        print("exception added")
                        exceptions[NameExceptionType.MIDDLE_INITIAL].append(folder)
                        similarityFound = True

                else:
                    print("exception added")
                    exceptions[NameExceptionType.NO_MIDDLE_INITIAL].append(folder)
                    similarityFound = True

            else:
                if patient.isException and patient.middleInitial:
                    print("exception added")
                    exceptions[NameExceptionType.NO_MIDDLE_INITIAL].append(folder)
                    similarityFound = True
                else:
                    directory = folder
                    break

        elif (patient.getFirstName().lower() == folderFirst and isSimilar(patient.getLastName().lower(), folderLast, .25)) or (isSimilar(patient.getFirstName().lower(), folderFirst, .25) and patient.getLastName().lower() == folderLast):
            if patient.isException:
                if patient.middleInitial == folderMiddle:
                    print("exception added")
                    exceptions[NameExceptionType.SPELLING].append(folder)
                    similarityFound = True
            else:
                print("exception added")
                exceptions[NameExceptionType.SPELLING].append(folder)
                similarityFound = True

    return directory, exceptions, similarityFound


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
            del lastName[suffixIndex:]

    if name[-1] == "." and name[-3] == " " and name[-2].isalpha():
        middleInitial = name[-2].strip().lower()

    return firstName, lastName, middleInitial, suffix


def handleDirectoryExceptions(exceptions, patient):
    folderNum = 2
    folderList = []

    for nameExceptionType in exceptions:
        if exceptions[nameExceptionType]:
            match nameExceptionType:
                case NameExceptionType.NO_MIDDLE_INITIAL:
                    print("\nFor the following folders, either the file or folder includes a middle initial while the other does not:")
                case NameExceptionType.MIDDLE_INITIAL:
                    print("\nThese folders have different middle initials from the file:")
                case NameExceptionType.SPELLING:
                    print("\nThere are minor spelling changes between the file and the following folders:")

            for folder in exceptions[nameExceptionType]:
                print(f"{folderNum}: {folder.name}")
                folderList.append(folder)
                folderNum += 1

    if folderNum > 2:
        print("\nAbove are all of the found folders with a similar name to the detected patient.")
        print("Type a number from an folder and press enter to place the file there.")

    print("\nChoose 1 to create a new folder for the patient.")
    print("Choose 0 to place the file in the same folder as the originally analyzed document.\n")

    choice = -1
    while choice < 0 or choice >= folderNum:
        if folderNum > 3:
            print(f"0, 1, or a folder from 2 - {folderNum - 1}:", end=" ")
        elif folderNum == 3:
            print(f"0, 1, or 2:", end=" ")
        else:
            print("0 or 1:", end=" ")

        while True:
            try:
                choice = int(input())
                break
            except ValueError:
                print("Only enter numbers.")


    if choice >= 2:
        choice -= 2
        return folderList[choice]
    elif choice == 1:
        return Path(Settings.foldersDirectory) / (patient.getName() + ".pdf")
    else:
        return ""
    

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