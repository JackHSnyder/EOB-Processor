class Date:
    def __init__(self, month=1, day=1, year=0, force=False):
        if not force:
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
                
            if day < 1 or day > 31:
                raise ValueError("Day must be between 1 and 31")

            if year > 2000:
                year -= 2000
            if year < 0 or year > 100:
                raise ValueError("Year must be between 2000 and 2100")
            

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

Date.null = Date(0, 0, 0, force=True)