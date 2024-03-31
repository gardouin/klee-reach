//===-- StateInformation.h ------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef KLEE_STATE_INFORMATION_H
#define KLEE_STATE_INFORMATION_H

#include <unordered_map>

namespace klee {
  /// This structure represents all information regarding a state:
  ///   - the current line of the current instruction
  ///   - the depth of the state (i.e. depth of the branch)
  ///   - a map with the counter of executions for each instruction
  ///   - a map with elementary depth for each instruction
  class StateInformation {
    unsigned int currentLine = 0;
    int depth = 0;
    int gMax = 0; // current max elementary depth
    std::unordered_map<unsigned int, int> executedLines;
    std::unordered_map<unsigned int, int> gVal;

  public:
    unsigned int getCurrentLine();
    int getDepth();
    std::unordered_map<unsigned int, int> getExecutedLines();
    int getGMax();
    std::unordered_map<unsigned int, int> getGVal();

    void setCurrentLine(unsigned int);
    void setDepth(int);
    void setGMax(int);
    void setGVal(unsigned int, int);

    void copyExecutedLines(std::unordered_map<unsigned int, int>);
    void copyGVal(std::unordered_map<unsigned int, int>);

    void incrDepth();
    void updateExecutedLines();
  };
} // klee namespace

#endif /* KLEE_STATE_INFORMATION_H */
