from Date import Date

class Patient:
    medicare = ""

    def __init__(self, firstName = "", lastName = "", middleInitial = "", date : Date = Date.null):
        self.firstName = firstName.capitalize()
        self.lastName = lastName.capitalize()
        self.middleInitial = middleInitial.capitalize()

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

    def setException(self):
        self.isException = True


    def getFirstLastName(self):
      return f"{self.lastName}, {self.firstName}"
    

    def __str__(self):
        middle = f" {self.middleInitial}." if self.middleInitial and self.isException else ""
        startDOS = str(self.startDOS)[:5] if self.startDOS.isSameYear(self.endDOS) else str(self.startDOS)
        dos = f"{startDOS}-{self.endDOS}" if self.endDOS != Date.null else startDOS

        return f"{self.lastName}, {self.firstName}{middle} - {self.medicare}DOS {dos}"
    

    def __eq__(self, other):
        return (self.firstName == other.firstName and
                self.lastName == other.lastName and
                self.middleInitial == other.middleInitial)