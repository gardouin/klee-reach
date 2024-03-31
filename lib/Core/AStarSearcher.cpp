//===-- AStarSearcher.cpp -------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#include "AStarSearcher.h"
#include "ExecutionState.h"

#include "klee/ADT/FibonacciHeap.h"
#include "klee/Module/InstructionInfoTable.h"
#include "klee/Module/KInstruction.h"
#include "klee/Module/KModule.h"

#include <cassert>

using namespace klee;
using namespace llvm;


/// ASTARSEARCHER

float AStarSearcher::computePriority(ExecutionState *state) {
  // looking for the distance between the instruction and the target
  // if not found, dist = inf
  float dist = findValue(distanceMap, state->pc->info->assemblyLine);
  return dist + statesInformation[state].getDepth();
}

ExecutionState &AStarSearcher::selectState() {
  ExecutionState *selected = states.top().value;
  if (enabledPrintWorklist()) // debugging tool
    printWorklist(selected);
  return *selected;
}

void AStarSearcher::update(ExecutionState *current,
                           const std::vector<ExecutionState *> &addedStates,
                           const std::vector<ExecutionState *> &removedStates) {
  // collect distance map (only at the beginning of the execution)
  if (current == 0) {
    distanceMap = parseDistFile();
  }

  // NOTE: states must be inserted BEFORE the current state is updated
  // New states are forked versions of the current state: therefore, state 
  // information must be updated afterwards, for each state independently

  // insert states
  for (const auto state : addedStates) {
    // copying state information (before taking the branch)
    copyStateInformation(current, state);
    // updating state information (when taking the branch)
    updateStateInformation(state);

    // creating the HeapElement for the new state
    HeapElement newState { computePriority(state), state };
    FibonacciHeap::handle_type handle = states.push(newState);
    handlesMap[state] = handle;
  }

  // update current
  if (current != 0) {
    updateStateInformation(current);
    // replacing the current state by an updated version in the heap
    HeapElement updatedState = { computePriority(current), current };
    states.update(handlesMap[current], updatedState);
  }

  // remove states
  for (const auto state : removedStates) {
    if (state != states.top().value) {
      assert(handlesMap.find(state) != handlesMap.end() && "invalid state removed");
      states.erase(handlesMap[state]);
      handlesMap.erase(state);
    } else {
      states.pop();
    }
  }
}

bool AStarSearcher::empty() {
  return states.empty();
}

void AStarSearcher::printName(llvm::raw_ostream &os) {
  os << "AStarSearcher\n";
}

void AStarSearcher::updateStateInformation(ExecutionState *state) {
  StateInformation &stateInfo = statesInformation[state];
  // updating current line
  stateInfo.setCurrentLine(state->pc->info->assemblyLine);
  // incrementing the depth of the state
  stateInfo.incrDepth();
}

/// Deep copy of some state information
void AStarSearcher::copyStateInformation(ExecutionState *src, ExecutionState *dest) {
  StateInformation &destSI = statesInformation[dest];
  StateInformation &srcSI = statesInformation[src];

  if (src != 0) {
    destSI.setDepth(srcSI.getDepth());
  }
}

// Debug method for printing the worklist
void AStarSearcher::printWorklist(ExecutionState *selected) {
  llvm::raw_ostream *stream = &llvm::errs();

  (*stream) << "Selecting a new state...\n";
  (*stream) << "Current worklist:\n";

  (*stream) << "[\n";
  for (const HeapElement state : states) {
    (*stream) << "\t(" << state.value->id << ") [prio=" 
    << state.priority << "] l"
    << state.value->pc->info->assemblyLine << ": " 
    << *(state.value->pc->inst) << " (@"
    << state.value->pc->getSourceLocation()
    << printStateInfo(state)
    << " | dist: "
    << findValue(distanceMap, state.value->pc->info->assemblyLine)
    << ")\n";
  }
  (*stream) << "]" << '\n';
  (*stream) << "Selected state: " << (selected)->id << "\n\n";
}

std::string AStarSearcher::printStateInfo(HeapElement state) {
  return "| depth: " + std::to_string(statesInformation[state.value].getDepth());
}


/// ASTAR2SEARCHER

float AStar2Searcher::computePriority(ExecutionState *state) {
  StateInformation &stateInfo = statesInformation[state];
  unsigned int currentLine = stateInfo.getCurrentLine();
  float dist = findValue(distanceMap, currentLine);
  int g = stateInfo.getGVal()[currentLine];
  return g * lambda(stateInfo.getExecutedLines()[currentLine], g) + dist;
}

void AStar2Searcher::printName(llvm::raw_ostream &os) {
  os << "AStar2Searcher\n";
}

void AStar2Searcher::updateStateInformation(ExecutionState *state) {
  // same updates as for AStarSearcher (i.e. current line & depth)
  AStarSearcher::updateStateInformation(state);
  
  StateInformation &stateInfo = statesInformation[state];
  unsigned int currentLine = stateInfo.getCurrentLine();

  // updating g (elementary depth)
  if (stateInfo.getGVal().find(currentLine) == stateInfo.getGVal().end()) {
    stateInfo.setGMax(stateInfo.getGMax() + 1);
    stateInfo.setGVal(currentLine, stateInfo.getGMax());
  }
  // adding 1 to the number of executions of the current line
  stateInfo.updateExecutedLines();
}

/// Deep copy of some state information
void AStar2Searcher::copyStateInformation(ExecutionState *src, ExecutionState *dest) {
  // copying depth
  AStarSearcher::copyStateInformation(src, dest);

  StateInformation &destSI = statesInformation[dest];
  StateInformation &srcSI = statesInformation[src];
  
  if (src != 0) {
    destSI.setGMax(srcSI.getGMax());
    destSI.copyGVal(srcSI.getGVal());
    destSI.copyExecutedLines(srcSI.getExecutedLines());
  }
}

float AStar2Searcher::lambda(int mu, int g) {
  if (mu <= g) {
    return 0;
  }
  return std::log10(mu - (g - 1)) / 10;
}

// Debug method for printing the worklist
std::string AStar2Searcher::printStateInfo(HeapElement state) {
  return AStarSearcher::printStateInfo(state) +
         " | g: " +
         std::to_string(statesInformation[state.value].getGVal()[state.value->pc->info->assemblyLine]) +
         " | mu: " +
         std::to_string(statesInformation[state.value].getExecutedLines()[state.value->pc->info->assemblyLine]);
}
