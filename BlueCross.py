import re

import helper
from Patient import Patient
from Date import Date

class BlueCross:
    def shapeDocument(doc):
        croppedDoc = []

        for page in doc:
            width = page.shape[1]
            croppedPage = page[:, :int(width * 0.275)]  # Cut off the right 72.5% of the page
            croppedDoc.append(croppedPage)

        return croppedDoc

    def extractPatients(wordArray):
        patients = []
        tempPatient = Patient()

        startIndex = next((i for i, value in enumerate(wordArray) if value == "923"), -1)
        # Loop for each potential patient
        while startIndex != -1:
            count = 0
            nameIndex = startIndex + 1
            namePart = wordArray[nameIndex]
            nameArray = []

            # Loop for each part of the name (unless it's unreasonably long)
            while count < 6:
                nameParts = [part for part in re.split(r'[_-]', namePart) if part]  # Removes instances of "_" from the current string - OCR sometimes registers the below line as an extra "." or "_"
                if len(nameParts) > 1:
                    for i in range(1, len(nameParts)):
                        wordArray.insert(nameIndex + i, nameParts[i])
                    del nameParts[1:]

                if len(nameParts) == 1:
                    namePart = nameParts[0]

                    if len(nameArray) >= 2 and namePart == nameArray[0]:
                        break
                    elif "\n" in namePart:
                        print("Newline found")
                        break

                    nameArray.append(namePart)
                    count += 1

                nameIndex += 1
                namePart = wordArray[nameIndex]

            del wordArray[:nameIndex]

            if count > 5:
                continue


            lastNameArray = []
            firstNameArray = []
            isFirstName = False

            i = 0
            # Loop through each part of the discovered name to find first-last
            while i < len(nameArray):
                name = nameArray[i]
                nameParts = [part for part in re.split(r'[,.]', name) if part]  # Removes instances of "," or "." from the current string - OCR sometimes registers the below line as extra punctuation or mistakes "," for "."
                print(nameParts)
                if len(nameParts) != 0:
                    if helper.isNameSuffix(nameParts[0]):
                        for name in firstNameArray:
                            lastNameArray.append(name)

                        firstNameArray = []
                        lastNameArray.append(nameParts[0])

                        isFirstName = True

                    elif not isFirstName:
                        lastNameArray.append(nameParts[0])

                        if len(nameParts) > 1 or len(name) != len(nameParts[0]):
                            isFirstName = True

                    else:
                        firstNameArray.append(nameParts[0])

                    for j in range(1, len(nameParts[1:])):
                        nameArray.insert(i + j, nameParts[j])

                i += 1

            if len(firstNameArray) == 0:
                firstNameArray = lastNameArray[1:]
                del lastNameArray[1:]

            if len(firstNameArray[-1]) == 1:
                tempPatient.setMiddleInitial(firstNameArray[-1])
                firstNameArray.pop()

            for name in lastNameArray:
                tempPatient.addToLastName(name)
            for name in firstNameArray:
                tempPatient.addToFirstName(name)


            dateIndex = next((i for i, value in enumerate(wordArray) if value == "SPINE"), -1)
            nextNameIndex = next((i for i, value in enumerate(wordArray) if value == "923"), -1)
            dateFound = False

            while dateIndex != -1 and (dateIndex < nextNameIndex or nextNameIndex == -1):
                if wordArray[dateIndex + 2] == "SPORT" or wordArray[dateIndex + 3] == "PHYSICAL":
                    potentialDate = wordArray[dateIndex + 5]
                    date = potentialDate.replace("/", "")

                    if len(potentialDate) == 10 and len(date) == 8 and date.isdigit():
                        tempPatient.newDOS(Date(int(date[:2]), int(date[2:4]), int (date[6:])))
                        dateFound = True
                        break
                    else:
                        del wordArray[dateIndex]

                dateIndex = next((i for i, value in enumerate(wordArray) if value == "SPINE"), -1)

            if (dateFound):
                helper.recordService(patients, tempPatient)

            tempPatient = Patient()
            startIndex = next((i for i, value in enumerate(wordArray) if value == "923"), -1)

        return patients