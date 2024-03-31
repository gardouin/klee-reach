//===-- AStarUtils.h ------------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef KLEE_ASTAR_UTILS_H
#define KLEE_ASTAR_UTILS_H

#include "klee/ADT/FibonacciHeap.h"

#include <fstream>
#include <string>
#include <unordered_map>

namespace klee {

  bool enabledPrintWorklist();
  
  float findValue(std::unordered_map<int, int>, int);
  
  std::unordered_map<int, int> parseDistFile();

} // klee namespace

#endif /* KLEE_ASTAR_UTILS_H */
