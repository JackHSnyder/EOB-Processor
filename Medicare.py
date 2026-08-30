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
    
        for word in wordArray:
            match state:
                case ParseState.SEARCHING:
                    if word == "NAME":
                        state = ParseState.LAST_NAME
    
                    continue
    
                case ParseState.LAST_NAME:
                    parts = re.split(r'[,.]', word, maxsplit=1)  # Split the word at the first comma or period

                    if len(parts) == 1:
                        tempPatient.addToLastName(parts[0])
    
                    else:
                        tempPatient.addToLastName(parts[0])
                        tempPatient.addToFirstName(parts[1])
    
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