# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B2

# Tabulation Asymptotic Complexity

# Run A3 on strings of growing length n, using |A| = |B| = n. Test the following values of n
# [10,20,40,80,160,320,640,1280]. Fill in a table with the following headers: 
# [n, total_ops, ratio, run time (ms), ratio]. 

# Plot total_operations against n on log-log axes. Do the same for run time 
# (separate graphs of course). When does the ratio between consecutive points stabilize (if it does)?

from study.study import Study
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from edit_distance.table import TabulatedEditDistance

class CaseB2(Study):
    def run(self) -> None:
        # Run naive and memoized implementations, collect results, plot them.
        ...

def main() -> None:
    CaseB2().run()

if __name__ == "__main__":
    main()