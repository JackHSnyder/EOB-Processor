import helper
from Patient import Patient
from Date import Date


class Medicare:
    def shapeDocument(doc):
        croppedDoc = []

        for page in doc:
            width = page.shape[1]
            croppedPage = page[:, :int(width * 0.5)]  # Cut off the right 50% of the page
            croppedDoc.append(croppedPage)

        return croppedDoc

    def extractPatients(wordArray):
        patients = []
        tempPatient = Patient()


        startIndex = helper.findNext(wordArray, "NAME")
        # Loop for each potential patient
        while startIndex != -1:
            count = 0
            nameIndex = startIndex + 1
            namePart = wordArray[nameIndex]
            nameArray = []

            # Loop for each part of the name (unless it's unreasonably long)
            while count < 6:
                nameParts = helper.splitAt(namePart, "_-", 0)  # Removes instances of "_" from the current string - OCR sometimes registers the below line as an extra "." or "_"
                if len(nameParts) > 1:
                    for i in range(1, len(nameParts)):
                        wordArray.insert(nameIndex + i, nameParts[i])

                    del nameParts[1:]

                if len(nameParts) == 1:
                    namePart = nameParts[0]

                    if namePart == "\n":
                        break
                    elif namePart == "MID":
                        break
                    elif namePart == "ACNT":
                        del nameArray[-2:]
                        break

                    nameArray.append(namePart)
                    count += 1

                nameIndex += 1
                namePart = wordArray[nameIndex]

            del wordArray[:nameIndex + 1]

            if count > 5:
                continue


            lastNameArray = []
            firstNameArray = []
            isFirstName = False

            i = 0
            # Loop through each part of the discovered name to find first-last
            while i < len(nameArray):
                name = nameArray[i]
                nameParts = helper.splitAt(name, ",.", 0)  # Removes instances of "," or "." from the current string - OCR sometimes registers the below line as extra punctuation or mistakes "," for "."
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

            if len(firstNameArray) > 0 and len(firstNameArray[-1]) == 1:
                tempPatient.setMiddleInitial(firstNameArray[-1])
                firstNameArray.pop()

            for name in lastNameArray:
                tempPatient.addToLastName(name)
            for name in firstNameArray:
                tempPatient.addToFirstName(name)


            dateIndex = helper.findNext(wordArray, "11")
            nextNameIndex = helper.findNext(wordArray, "NAME")
            dateFound = False

            while dateIndex != -1 and (dateIndex < nextNameIndex or nextNameIndex == -1):
                date = wordArray[dateIndex - 1]
                
                # If the grabbed date fails, check if it works using part of the shortened version before it.
                # Otherwise, check if there is another date below it.
                # If all else fails, force the date to be valid.
                if date.isdigit() and len(date) == 6:
                    try:
                        dateObj = Date(int(date[:2]), int(date[2:4]), int(date[4:]))

                    except ValueError as e:
                        shortDate = wordArray[dateIndex - 2]
                        if shortDate.isdigit() and len(shortDate) == 4:
                            try:
                                dateObj = Date(int(shortDate[:2]), int(shortDate[2:]), int(date[4:]))
                            except ValueError as e:
                                print(f"Error parsing date: {e}")
                                del wordArray[:dateIndex + 1]
                                potentialDateIndex = helper.findNext(wordArray, "11")

                                if potentialDateIndex != -1 and (potentialDateIndex < nextNameIndex or nextNameIndex == -1):
                                    dateIndex = potentialDateIndex
                                    continue
                                else:
                                    dateObj = Date(int(date[:2]), int(date[2:4]), int(date[4:]), force=True)


                    tempPatient.newDOS(dateObj)
                    dateFound = True
                    del wordArray[:dateIndex + 1]

                    break
                else:
                    del wordArray[:dateIndex + 1]

                dateIndex = helper.findNext(wordArray, "11")

            if dateFound:
                helper.recordService(patients, tempPatient)

            tempPatient = Patient()
            startIndex = helper.findNext(wordArray, "NAME")

        return patients