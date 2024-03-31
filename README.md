KLEE-Reach
==========

`KLEE-Reach` is an extension to KLEE that allows you to perform
reachability analysis with KLEE. In particular, this new version offers
two new heuristics inspired by A* and developed to improve the 
efficiency of symbolic execution in target search.

## Requirements

In addition to the KLEE requirements, installation of this extension 
requires the following:
- Boost C++ library
- Python 3.8 and pip

## Installation

To install KLEE-Reach, simply follow the usual instructions for building
KLEE. Instead of following these steps on the official KLEE repository, 
use our repository.

In addition to that, execute `make` in klee-reach-utils. This will 
install the Python module for calculating distances.

## How to use

Please refer to `user_manual.pdf`.

## References

The original project: http://klee-se.org/

The paper that developed the new heuristics: 
https://doi.org/10.1007/978-3-031-47115-5_4
