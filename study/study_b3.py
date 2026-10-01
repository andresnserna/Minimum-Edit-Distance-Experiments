# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B3

# Memoized vs. Tabulated

# Compare A2 and A3 on identical inputs across all of:
# - total_operations
# - Run time (ms)
# - table cells allocated, for A3 this will be the size of the full table; for A2 it will be the
#   number of memo entries actually created (is there a formula to find this, or is it input dependent?)
# - maximum recursion depth reached for A2

# These two implementations compute the same recurrence and will have very similar operation
# counts. If your implementations are correct, the operation counts should be similar, but what
# about their run times? The number of cells allocated?