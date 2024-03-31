# KLEE-REACH-DIST
---

The purpose of this Python library is to compute a `.dist` file containing the 
distances between an LLVM instruction and a target instruction in the same LLVM
file.

This library was primarly developped to assist KLEE's A-star heuristic.

# Installation
---

Run
```
make install
```

# Uninstallation
---

Run
```
make uninstall
```

# How to run KLEE-Reach
---

After specifying the path to the KLEE executable (built from the "reach" 
version) in `klee-reach.sh`, simply use the script as if you wanted to use 
KLEE (same command line format). A few options are added, in particular 
concerning the choice of heuristic:
- `-a` : using A-star searcher
- `-A` : using A-star2 searcher 
- `-k` : using KLEE default search heuristic

If you don't specify an argument, A-star2 will be the search heuristic.

See `./klee-reach.sh -h` for more information.
