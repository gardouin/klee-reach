//===-- FibonacciHeap.h ---------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef __FIBONACCI_HEAP__
#define __FIBONACCI_HEAP__

#include <boost/heap/fibonacci_heap.hpp>

#define INF std::numeric_limits<float>::infinity()

namespace klee {
	class ExecutionState;
}

using namespace klee;

/// Wrapper for ExecutionState in the worklist
struct HeapElement {
	float priority;
	ExecutionState * value;
} typedef HeapElement;

struct compare {
	bool operator()(const HeapElement &l, const HeapElement &r) const {
		return l.priority > r.priority;
	}
};

// NOTE: if you want to change the implementation of the data structure (and get
// rid of Boost for instance), simply define it and replace the following typedef
// by your own implementation
// Please not that your own implementation must respect the ADT of the boost 
// FibonacciHeap if you hope to not modify the source code.
// You must also use the HeapElement as the element type of your worklist

typedef boost::heap::fibonacci_heap<HeapElement, boost::heap::compare<compare>> FibonacciHeap;

#endif
