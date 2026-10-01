# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B1

# When does Naive become unusable?

# Run A1 against A2 on inputs of increasing length. Capture both operation counts and run time.
# Find and report the input size at which the naive version becomes impractical on your machine 
# — define "impractical" yourself and state your threshold (e.g. >60 seconds). Plot both
# implementations on shared axes.

# Report calls for both.