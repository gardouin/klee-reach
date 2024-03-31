//===-- AStarUtils.cpp ----------------------------------------------------===//
//
//                     KLEE-REACH
//
// Copyright (C) 2024 Université de Bordeaux, Bordeaux INP, CNRS
// See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//


#include "AStarUtils.h"

#include "llvm/Support/CommandLine.h"

using namespace klee;
using namespace llvm;

/// KLEE command line options

namespace klee {
  cl::OptionCategory AStarCat("AStar options",
                              "These are KLEE-Reach options.");

  cl::opt<std::string> InputDistanceFile(
      "input-distance-file",
      cl::desc("Specify the path to the distance file"),
      cl::init(""),
      cl::cat(AStarCat));

llvm::cl::opt<bool> DebugPrintWorklist(
    "debug-print-worklist",
    llvm::cl::desc("Display worklist during execution (A-star searchers only)"),
    llvm::cl::CommaSeparated,
    cl::cat(AStarCat));
}

bool klee::enabledPrintWorklist() {
  return DebugPrintWorklist;
}


///

/// Returns INF if no value found
float klee::findValue(std::unordered_map<int, int> map, int key) {
  if (map.find(key) == map.end()) {
    return INF;
  }
  return map[key];
}

void splitLine(std::string line, int &line_number, int &dist_value) {
  size_t pos = line.find(":");
  line_number = std::stoi(line.substr(0, pos));
  line.erase(0, pos+1);
  pos = line.find(":");
  dist_value = std::stoi(line.substr(0, pos));
}

/// Parses the .dist file and returns the distance map
std::unordered_map<int, int> klee::parseDistFile() {
  std::ifstream file;
  std::string line;
  std::unordered_map<int, int> distances;
  std::string fileName = InputDistanceFile;
  llvm::raw_ostream *stream = &llvm::errs();

  if (fileName != "") {
    (*stream) << "[AStar] Starting collecting distance map (" << fileName << ")...\n";
    file.open(fileName);
    
    int line_number;
    int dist_value;

    if (file.is_open()) {
      while (file) {
        std::getline(file, line);
        if (line != "") {
          splitLine(line, line_number, dist_value);
          distances[line_number] = dist_value;
        }
      }
      (*stream) << "[AStar] Done\n";
    } else {
      (*stream) << "[AStar] Couldn't open file\n";
    }
  } else {
    (*stream) << "[AStar] No distance file given... All distances are considered infinite.\n" 
    << "[AStar] Usage: --input-distance-file=<path>\n";
  }
  return distances;
}
