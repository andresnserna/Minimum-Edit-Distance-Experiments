# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B4

# Cost weights

# Run each of the following cost schemes against the same input set. Report, for each scheme
# and each string pair: the distance, and the composition of the optimal edit script (counts of S, I,
# D, and matches).

# Scheme sub ins del
# S1      1   1   1
# S2      2   1   1
# S3      3   1   1
# S4      1   1   5

# Then answer these three questions in your report.
#    (a) The substitution threshold. Across S1-S3, substitution should go from common to
# completely absent. State the general condition on the three costs under which substitution can
# appear in some optimal script, and prove it in a short paragraph. This should be a succinct
# argument, not a research paper

#    (b) The LCS identity. Under S3, verify that for every pair in your data,
# distance(A, B) = |A| + |B| − 2 · LCS(A, B)
# Computer LCS using our code from September 17th. Explain why this identity holds when
# substitution is dominated and fails when it is not.

#    (c) Symmetry. Under S4, find a concrete pair where distance(A, B) ≠ distance(B, A).
# Explain why. Then state the condition on the costs under which edit distance is symmetric.

# Methodology requirements

# Your report must state: machine (CPU, RAM, OS), programming language and version,
# repetitions per data point and how you aggregated them (mean, median, maximum and
# minimum, etc), whether warm-up runs were discarded, and how input strings were generated.