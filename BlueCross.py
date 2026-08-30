import string

import helper
from enums import ParseState
from Patient import Patient
from Date import Date

class BlueCross:
    def extractPatients(wordArray):
            patients = []
            tempPatient = Patient()
            lastFirstName = ""
            state = ParseState.SEARCHING
            found923 = False  # Used to check if the word after 923 is "SPINE"
        
            for word in wordArray:
                match state:
                    case ParseState.SEARCHING:
                        if word == "923":
                            state = ParseState.LAST_NAME
                            found923 = True
        
                        continue
        
                    case ParseState.LAST_NAME:
                        if found923:
                            found923 = False

                            if word == "SPINE":
                                state = ParseState.SEARCHING
                                continue

                        if word.find(",") == -1:
                            tempPatient.addToLastName(word)
        
                        else:
                            ln, fn = helper.splitAtChar(word, ",")  # "fn" is blank if the names were correctly spaced
                            tempPatient.addToLastName(ln)
                            tempPatient.addToFirstName(fn)
        
                            state = ParseState.FIRST_NAME
        
                        continue
        
                    case ParseState.FIRST_NAME:
                        word = word.translate(str.maketrans("", "", string.punctuation))  # Removes any punctuation from the current word - OCR sometimes registers below line as extra "." or "_"

                        if not lastFirstName:
                            lastFirstName = word
        
                        elif len(lastFirstName) == 1 and len(word) != 1:
                            tempPatient.setMiddleInitial(lastFirstName)

                            state = ParseState.DOS
        
                        else:
                            tempPatient.addToFirstName(lastFirstName)
                            lastFirstName = word
        
                        continue
        
                    case ParseState.DOS:
                        # Dates are always MM/DD/YYYY
                        if len(word) == 10:
                            potentialDate = word.replace("/", "")

                            if len(potentialDate) == 8 and potentialDate.isdigit():
                                tempPatient.newDOS(Date(int(potentialDate[:2]), int(potentialDate[2:4]), int (potentialDate[4:])))

                                state = ParseState.SEARCHING
                                helper.recordService(patients, tempPatient)
                                tempPatient = Patient()
                                lastFirstName = ""
        
                        continue
        
            return patients