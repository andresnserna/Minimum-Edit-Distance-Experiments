import time

class TimeTracker:
    """
    
    """
    def __init__(self):
        self.time_START = 0.0
        self.time_FINISH = 0.0
        self.total_TIME = 0.0
        self.function_name = ""

    def reset(self):
        self.time_START = 0.0
        self.time_FINISH = 0.0
        self.total_TIME = 0.0
        self.function_name = ""

    def check(self):
        return self.total_TIME == (self.time_FINISH - self.time_START)

    def start(self):
        self.time_START = time.perf_counter()

    def finish(self):
        self.time_FINISH = time.perf_counter()
        self.total_TIME = self.time_FINISH - self.time_START


    def as_dict(self):
        return {
            "function_name": self.function_name,
            "time_START": self.time_START,
            "time_FINISH": self.time_FINISH,
            "total_TIME": self.total_TIME,
        }

    def __repr__(self):
        return (f"TimeTracker(function_name='{self.function_name}', total_TIME={self.total_TIME}, "
                f"check={'OK' if self.check() else 'MISMATCH'})")