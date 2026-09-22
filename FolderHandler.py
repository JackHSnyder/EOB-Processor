from pathlib import Path

import helper
import Settings
from enums import NameExceptionType

class FolderHandler:
    def findDirectory(patientFolders, patient):
        directory = ""

        # Creates a list of tuples which are required to have the type NameExceptionType and then str
        exceptions: dict[NameExceptionType, list[Path]] = {
            NameExceptionType.DUPLICATE: [],
            NameExceptionType.NO_MIDDLE_INITIAL: [],
            NameExceptionType.MIDDLE_INITIAL: [],
            NameExceptionType.SPELLING: []
        }

        for folder in patientFolders:
            folderFirst, folderLast, folderMiddle, _suffix_ = helper.parseFullName(str(folder.name))
            if patient.getFirstName().lower() == folderFirst and patient.getLastName().lower() == folderLast:
                if folderMiddle:
                    if patient.middleInitial:
                        if patient.middleInitial.lower() == folderMiddle:
                            directory = FolderHandler.exactDirectoryFound(exceptions, directory, folder)

                        else:
                            exceptions[NameExceptionType.MIDDLE_INITIAL].append(folder)

                    else:
                        exceptions[NameExceptionType.NO_MIDDLE_INITIAL].append(folder)

                else:
                    if patient.isException and patient.middleInitial:
                        exceptions[NameExceptionType.NO_MIDDLE_INITIAL].append(folder)
                    else:
                        directory = FolderHandler.exactDirectoryFound(exceptions, directory, folder)

            elif (patient.getFirstName().lower() == folderFirst and helper.isSimilar(patient.getLastName().lower(), folderLast, .25)) or (helper.isSimilar(patient.getFirstName().lower(), folderFirst, .25) and patient.getLastName().lower() == folderLast):
                if patient.isException:
                    if patient.middleInitial.lower() == folderMiddle:
                        exceptions[NameExceptionType.SPELLING].append(folder)
                else:
                    exceptions[NameExceptionType.SPELLING].append(folder)

        return directory, exceptions

    # Checks if the directory was already set, and if so, makes both the directory and the new folder an exception
    def exactDirectoryFound(exceptions, directory, folder):
        if directory or exceptions[NameExceptionType.DUPLICATE]:
            if not exceptions[NameExceptionType.DUPLICATE]:
                exceptions[NameExceptionType.DUPLICATE].append(directory)
                directory = ""
            exceptions[NameExceptionType.DUPLICATE].append(folder)
        else:
            directory = folder

        return directory


    def handleDirectoryExceptions(exceptions, patient):
        folderNum = 2
        folderList = []

        for nameExceptionType in exceptions:
            if exceptions[nameExceptionType]:
                match nameExceptionType:
                    case NameExceptionType.DUPLICATE:
                        print("\nMultiple folders with the same correct name were found:")
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
            return Path(Settings.foldersDirectory) / patient.getName()
        else:
            return ""