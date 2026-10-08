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
        self.cells_allocated = 0
        self.max_recursion_depth = 0

    def _increment(self, *, reads: int = 0, writes: int = 0, comparisons: int = 0) -> None:
        """Internal helper for counting a specific event by its exact resource cost."""
        self.reads += reads
        self.writes += writes
        self.comparisons += comparisons
        self.total_operations += reads + writes + comparisons

    def reset(self) -> None:
        self.reads = 0
        self.writes = 0
        self.comparisons = 0
        self.calls = 0
        self.total_operations = 0
        self.cells_allocated = 0
        self.max_recursion_depth = 0

    def record_cell_allocation(self, value: int = 1) -> None:
        """Record allocated DP cells or newly populated memo entries."""
        self.cells_allocated += value

    def record_recursion_depth(self, depth: int) -> None:
        """Track the deepest active recursive call level."""
        self.max_recursion_depth = max(self.max_recursion_depth, depth)

    def record_table_or_memo_read(self, value: int = 1) -> None:
        """Count one DP table or memo cell read.

        This event models a single read of an already-computed value from the DP
        table or memo cache. It counts as 1 read and 1 total operation per unit
        of value, with a default of 1.
        """
        self._increment(reads=value)

    def record_table_or_memo_write(self, value: int = 1) -> None:
        """Count one DP table or memo cell write.

        This event models storing a newly computed value into the DP table or memo
        cache. It counts as 1 write and 1 total operation per unit of value, with
        a default of 1.
        """
        self._increment(writes=value)

    def record_character_read(self, value: int = 1) -> None:
        """Count one character read from an input string.

        This event represents fetching a single character from A or B while
        evaluating the recurrence. It counts as 1 read and 1 total operation per
        unit of value, with a default of 1.
        """
        self._increment(reads=value)

    def record_character_equality_check(self, value: int = 1) -> None:
        """Count the cost of checking whether two characters are equal.

        The comparison A[i] == B[j] requires reading both characters and then
        comparing them. This contributes 2 reads, 1 comparison, and 3 total
        operations per unit of value, with a default of 1.
        """
        self._increment(reads=2 * value, comparisons=value)

    def record_string_equality_check(self, string_a: str, string_b: str) -> None:
        """
        does x number of CHAR equality checks where x is the shortests string
        """
        chars_checked = min(len(string_a), len(string_b))
        self.record_minimum_of_k(2) #finding the minimum len between string A and B
        self.record_character_equality_check(chars_checked) # record a char equality check x amount of times, where x is the len of the shorter string



    def record_minimum_of_k(self, k: int, value: int = 1) -> None:
        """Count the comparison cost of taking the minimum of k candidate values.

        A minimum over k values requires k - 1 comparisons. The function is used
        for the event "take the minimum of k values" in the recurrence or DP
        selection logic.

        Args:
            k: Number of candidate values being compared.
            value: Number of repeated minimum-of-k events to count. The cost is
                scaled by this multiplier, with a default of 1.

        Raises:
            ValueError: If k is less than 1, because there are no valid values to
                compare.
        """
        if k < 1:
            raise ValueError("k must be at least 1 when recording a minimum-of-k event.")
        self._increment(comparisons=(k - 1) * value)

    def record_base_case_initialization(self, value: int = 1) -> None:
        """Count a base-case cell initialization.

        This event represents writing the sentinel or default value for a DP or
        memo cell before a recurrence begins. It counts as 1 write and 1 total
        operation per unit of value, with a default of 1.
        """
        self._increment(writes=value)

    def check(self) -> bool:
        return self.total_operations == (self.reads + self.writes + self.comparisons)

    def as_dict(self):
        return {
            "reads": self.reads,
            "writes": self.writes,
            "comparisons": self.comparisons,
            "calls": self.calls,
            "total_operations": self.total_operations,
            "cells_allocated": self.cells_allocated,
            "max_recursion_depth": self.max_recursion_depth,
        }

    def __repr__(self):
        return (f"Counters(reads={self.reads}, writes={self.writes}, "
                f"comparisons={self.comparisons}, calls={self.calls}, "
                f"total_operations={self.total_operations}, "
                f"cells_allocated={self.cells_allocated}, "
                f"max_recursion_depth={self.max_recursion_depth}, "
                f"check={'OK' if self.check() else 'MISMATCH'})")