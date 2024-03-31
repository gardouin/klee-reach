//===-- StateInformation.cpp ----------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#include "StateInformation.h"

using namespace klee;

unsigned int StateInformation::getCurrentLine() {
  return currentLine;
}

int StateInformation::getDepth() {
  return depth;
}

std::unordered_map<unsigned int, int> StateInformation::getExecutedLines() {
  return executedLines;
}

int StateInformation::getGMax() {
  return gMax;
}

std::unordered_map<unsigned int, int> StateInformation::getGVal() {
  return gVal;
}

void StateInformation::setCurrentLine(unsigned int line) {
  currentLine = line;
}

void StateInformation::setDepth(int d) {
  depth = d;
}

void StateInformation::setGMax(int g) {
  gMax = g;
}

void StateInformation::setGVal(unsigned int line, int val) {
  gVal[line] = val;
}

void StateInformation::copyExecutedLines(std::unordered_map<unsigned int, int> execLines) {
  for (auto e : execLines) {
    executedLines[e.first] = e.second;
  }
}

void StateInformation::copyGVal(std::unordered_map<unsigned int, int> g) {
  for (auto e : g) {
    gVal[e.first] = e.second;
  }
}

void StateInformation::incrDepth() {
  depth++;
}

void StateInformation::updateExecutedLines() {
  if (executedLines.find(currentLine) == executedLines.end()) {
    executedLines[currentLine] = 1;
  } else {
    executedLines[currentLine] += 1;
  }
}
