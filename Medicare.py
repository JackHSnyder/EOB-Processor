import string
import re

import helper
from enums import ParseState
from Patient import Patient
from Date import Date


class Medicare:
    def extractPatients(wordArray):
        patients = []
        tempPatient = Patient()
        lastFirstName = ""
        potentialDate = ""
        state = ParseState.SEARCHING

        startIndex = next((i for i, value in enumerate(wordArray) if value == "NAME"), -1)
        # Loop for each potential patient
        while startIndex != -1:
            count = 0
            nameIndex = startIndex + 1
            namePart = wordArray[nameIndex]
            nameArray = []

            # Loop for each part of the name (unless it's unreasonably long)
            while count < 6:
                nameParts = re.split(r'[_-]', namePart)  # Removes instances of "_" from the current string - OCR sometimes registers the below line as an extra "." or "_"
                if len(nameParts) > 1:
                    for i in range(1, len(nameParts)):
                        wordArray.insert(nameIndex + i, nameParts[i])
                elif len(nameParts) == 1:
                    namePart = nameParts[0]

                    if namePart == "MID":
                        break
                    if namePart == "ACNT":
                        del nameArray[-2:]
                        break

                    nameArray.append(namePart)
                    count += 1

                nameIndex += 1
                namePart = wordArray[nameIndex]

            if count > 5:
                nameArray = []

            firstNameArray = []
            isFirstName = False

            i = 0
            # Loop through each part of the discovered name to find first-last
            while i < len(nameArray):
                name = nameArray[i]
                nameParts = re.split(r'[,.]', name)  # Removes instances of "," or "." from the current string - OCR sometimes registers the below line as extra punctuation or mistakes "," for "."
                print(nameParts)
                if len(nameParts) != 0:
                    if not isFirstName:
                        tempPatient.addToLastName(nameParts[0])

                        if len(nameParts) > 1 or len(name) != len(nameParts[0]):
                            isFirstName = True

                    else:
                        firstNameArray.append(nameParts[0])

                    for j in range(1, len(nameParts[1:])):
                        nameArray.insert(i + j, nameParts[j])

            if len(firstNameArray[-1]) == 1:
                tempPatient.setMiddleInitial = firstNameArray[-1]
                firstNameArray.pop()

            for name in firstNameArray:
                tempPatient.addToFirstName(name)

            del wordArray[:nameIndex]

            dateIndex = next((i for i, value in enumerate(wordArray) if value == "11"), -1)
            nextNameIndex = next((i for i, value in enumerate(wordArray) if value == "NAME"), -1)
            dateFound = False
            while dateIndex != -1 and dateIndex < nextNameIndex:
                date = wordArray[dateIndex - 1]
                if date.isDigit() and len(date) == 6:
                    tempPatient.newDOS(Date(int(date[:2]), int(date[2:4]), int(date[4:])))
                    dateFound = True
                    break
                else:
                    del wordArray[dateIndex]

                dateIndex = next((i for i, value in enumerate(wordArray) if value == "11"), -1)

            if dateFound:
                helper.recordService(patients, tempPatient)

            tempPatient = Patient()



            

        # for word in wordArray:
        #     match state:
        #         case ParseState.SEARCHING:
        #             if word == "NAME":
        #                 state = ParseState.LAST_NAME
    
        #             continue

        #         case ParseState.Name:
    
        #         case ParseState.LAST_NAME:
        #             parts = re.split(r'[,.]', word, maxsplit=1)  # Split the word at the first comma or period

        #             if len(parts) == 1:
        #                 tempPatient.addToLastName(parts[0])
    
        #             else:
        #                 tempPatient.addToLastName(parts[0])
        #                 tempPatient.addToFirstName(parts[1])
    
        #                 state = ParseState.FIRST_NAME
    
        #             continue
    
        #         case ParseState.FIRST_NAME:
        #             word = word.translate(str.maketrans("", "", string.punctuation))  # Removes any punctuation from the current word - OCR sometimes registers below line as extra "." or "_"
    
        #             if not lastFirstName:
        #                 lastFirstName = word
    
        #             elif word == "MID":
        #                 if len(lastFirstName) == 1:
        #                     tempPatient.setMiddleInitial(lastFirstName)
        #                 else:
        #                     tempPatient.addToFirstName(lastFirstName)
    
        #                 state = ParseState.DOS
    
        #             else:
        #                 tempPatient.addToFirstName(lastFirstName)
        #                 lastFirstName = word
    
        #             continue
    
        #         case ParseState.DOS:
        #             # Dates are always MMDD followed by MMDDYY in the following word
        #             if potentialDate != "":
        #                 if word[:4] == potentialDate and len(word) == 6 and word.isdigit():
        #                     potentialDate = ""
        #                     tempPatient.newDOS(Date(int(word[:2]), int(word[2:4]), int(word[4:])))
    
        #                     state = ParseState.SEARCHING
        #                     helper.recordService(patients, tempPatient)
        #                     tempPatient = Patient()
        #                     lastFirstName = ""
    
        #                 else:
        #                     potentialDate = ""
    
        #             if len(word) == 4 and word.isdigit():
        #                 potentialDate = word
    
        #             continue
    
        return patients