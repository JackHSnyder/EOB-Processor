from Date import Date

class Patient:
    medicare = ""

    def __init__(self, firstName = "", lastName = "", middleInitial = "", suffix = "", date : Date = Date.null):
        self.firstName = firstName.capitalize()
        self.lastName = lastName.capitalize()
        self.middleInitial = middleInitial.capitalize()
        self.suffix = suffix.capitalize()

        self.startDOS = date
        self.endDOS = Date.null

        self.isException = False

    def getFirstName(self):
        return self.firstName
    def setFirstName(self, fn):
        self.firstName = fn
    def addToFirstName(self, name):
        if name:
            if self.firstName:
                self.firstName += " " + name.capitalize()
            else:
                self.firstName = name.capitalize()

    def getLastName(self):
        return self.lastName
    def setLastName(self, ln):
        self.lastName = ln
    def addToLastName(self, name):
        if name:
            if self.lastName:
                self.lastName += " " + name.capitalize()
            else:
                self.lastName = name.capitalize()

    def setMiddleInitial(self, mi):
        self.middleInitial = mi.capitalize()

    def setSuffix(self, s):
        if s.upper() == "JR" or s.upper() == "SR":
            self.suffix = s.capitalize()
        else:
            self.suffix = s

    def newDOS(self, date : Date):
        if self.startDOS == Date.null:
            self.startDOS = date
        elif date < self.startDOS:
            if self.endDOS == Date.null:
                self.endDOS = self.startDOS
            self.startDOS = date
        elif date > self.endDOS:
            self.endDOS = date

    @staticmethod
    def setMedicare():
        Patient.medicare = "MC"

    # Means patient name was found in exception list; their middle initial will be displayed
    def setException(self):
        self.isException = True


    # Used for checking if the patient has their own folder when enabled
    def getName(self):
      middle = f" {self.middleInitial}" if self.middleInitial and self.isException else ""
      suffix = f" {self.suffix}" if self.suffix else ""
      return f"{self.lastName}{suffix}, {self.firstName}{middle}"
    


    def __str__(self):
        # Only add on the middle initial if patient is listed as a naming exception
        middle = f" {self.middleInitial}." if self.middleInitial and self.isException else ""
        # Add space before suffix if it exists
        suffix = f" {self.suffix}" if self.suffix else ""

        # Include the year twice only if the start and end DOS are in separate years
        startDOS = str(self.startDOS)[:5] if self.startDOS.isSameYear(self.endDOS) else str(self.startDOS)
        # Make the displayed date a range if there is an endDOS
        dos = f"{startDOS}-{self.endDOS}" if self.endDOS != Date.null else startDOS

        return f"{self.lastName}{suffix}, {self.firstName}{middle} - {self.medicare}DOS {dos}"
    

    def __eq__(self, other):
        return self.getName() == other.getName()