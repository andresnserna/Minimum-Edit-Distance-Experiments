# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

class Study:

   def __init__(self):
      raise NotImplementedError()

   def report_runtime() -> Str:
         # a bunch of sys calls that gather machine info, and then report it to the terminal in an organized way
         raise NotImplementedError()

   def generate_graph():
       # takes in the graph info from what ever scenario it is, then generates the graph associated
       raise NotImplementedError()

   

   
   