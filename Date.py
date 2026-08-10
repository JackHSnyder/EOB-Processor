class Date:
    def __init__(self, month, day, year):
        self.month = month
        self.day = day
        self.year = year

    def isSameYear(self, other):
        return self.year == other.year

    def __lt__(self, other):
        if self.year < other.year:
            return True
        elif self.year == other.year:
            if self.month < other.month:
                return True
            elif self.month == other.month:
                if self.day < other.day:
                    return True
        return False

    def __gt__(self, other):
        if self.year > other.year:
            return True
        elif self.year == other.year:
            if self.month > other.month:
                return True
            elif self.month == other.month:
                if self.day > other.day:
                    return True
        return False

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __str__(self):
        return f"{self.month:02d}.{self.day:02d}.{self.year:02d}"