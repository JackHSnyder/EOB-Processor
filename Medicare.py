import string

import helper
from enums import ParseState
import Patient
import Date


class Medicare:
    def extractPatients(wordArray):
        patients = []
        tempPatient = Patient()
        lastFirstName = ""
        potentialDate = ""
        state = ParseState.SEARCHING
    
        for word in wordArray:
            match state:
                case ParseState.SEARCHING:
                    if word == "NAME":
                        state = ParseState.LAST_NAME
    
                    continue
    
                case ParseState.LAST_NAME:
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
    
                    elif word == "MID":
                        if len(lastFirstName) == 1:
                            tempPatient.setMiddleInitial(lastFirstName)
                        else:
                            tempPatient.addToFirstName(lastFirstName)
    
                        state = ParseState.DOS
    
                    else:
                        tempPatient.addToFirstName(lastFirstName)
                        lastFirstName = word
    
                    continue
    
                case ParseState.DOS:
                    # Dates are always MMDD followed by MMDDYY in the following word
                    if potentialDate != "":
                        if word[:4] == potentialDate and len(word) == 6 and word.isdigit():
                            potentialDate = ""
                            tempPatient.newDOS(Date(int(word[:2]), int(word[2:4]), int(word[4:])))
    
                            state = ParseState.SEARCHING
                            helper.recordService(patients, tempPatient)
                            tempPatient = Patient()
                            lastFirstName = ""
    
                        else:
                            potentialDate = ""
    
                    if len(word) == 4 and word.isdigit():
                        potentialDate = word
    
                    continue
    
        return patients