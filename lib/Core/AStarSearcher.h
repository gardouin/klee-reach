//===-- AStarSearcher.h ---------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef KLEE_ASTARSEARCHER_H
#define KLEE_ASTARSEARCHER_H

#include "Searcher.h"
#include "AStarUtils.h"
#include "StateInformation.h"
#include "klee/ADT/FibonacciHeap.h"

#include <unordered_map>

namespace klee {
  class ExecutionState;

  /// AStarSearcher implements A-star style exploration. All states are kept in an order defined by a priority function. This function computes the priority according to the depth of the state and the distance between the current instruction and the target.
  class AStarSearcher : public Searcher {
    FibonacciHeap states;
    std::unordered_map<ExecutionState*, FibonacciHeap::handle_type> handlesMap;

  public:
    ExecutionState &selectState() override;
    void update(ExecutionState *current,
                const std::vector<ExecutionState *> &addedStates,
                const std::vector<ExecutionState *> &removedStates) override;
    bool empty() override;
    void printName(llvm::raw_ostream &os) override;

  protected:
    std::unordered_map<int, int> distanceMap;
    std::unordered_map<ExecutionState*, StateInformation> statesInformation;

    virtual float computePriority(ExecutionState *);
    virtual void updateStateInformation(ExecutionState *);
    virtual void copyStateInformation(ExecutionState *, ExecutionState *);
    virtual void printWorklist(ExecutionState *);
    virtual std::string printStateInfo(HeapElement);
  };

  /// AStar2Searcher implements an improved version of AStarSearcher. The only difference is the priority function: it now takes into account new metrics such as the number of occurrences of the state, the elementary depth, etc. This exploration method encourages exploration towards unknown instructions.
  class AStar2Searcher final : public AStarSearcher {
  public:
    void printName(llvm::raw_ostream &os) override;

  protected:
    float computePriority(ExecutionState *) override;
    void updateStateInformation(ExecutionState *);
    void copyStateInformation(ExecutionState *, ExecutionState *);
    float lambda(int, int);
    std::string printStateInfo(HeapElement);
  };

} // klee namespace

#endif /* KLEE_ASTARSEARCHER_H */
