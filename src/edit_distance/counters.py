class Counters:
    """
    Same convention as our sorting practice:
    reads/writes/comparisons are counted at each site that touches the 
    data. For this code we'll track total_operations is tracked 
    independently (not reads + writes + comparisons at the end of the method)
    check() can catch if you've missed or double-counted something.

    The calls datapoint counts invocations of find(), not each tick
    of the loop (like how we might have counted recursive calls).
    calls is not included in total_operations
    """
    def __init__(self):
        self.reads = 0
        self.writes = 0
        self.comparisons = 0
        self.calls = 0
        self.total_operations = 0

    def reset(self):
        self.reads = 0
        self.writes = 0
        self.comparisons = 0
        self.calls = 0
        self.total_operations = 0

    def check(self):
        return self.total_operations == (self.reads + self.writes + self.comparisons)

    def as_dict(self):
        return {
            "reads": self.reads,
            "writes": self.writes,
            "comparisons": self.comparisons,
            "calls": self.calls,
            "total_operations": self.total_operations,
        }

    def __repr__(self):
        return (f"Counters(reads={self.reads}, writes={self.writes}, "
                f"comparisons={self.comparisons}, calls={self.calls}, "
                f"total_operations={self.total_operations}, "
                f"check={'OK' if self.check() else 'MISMATCH'})")