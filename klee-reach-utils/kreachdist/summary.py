from kreachdist.datastructs.BasicBlock import BasicBlock
from kreachdist.datastructs.CFG import CFG
from kreachdist.datastructs.Program import Program
from kreachdist.utils.SCCGraph import build_dependency_graph
from kreachdist.utils.regex import extract_called_function, is_call
from kreachdist.utils.misc import get_last_instr, is_end_of_cfg

import math
import heapq
from typing import Mapping, List, Tuple

def summarize_functions(
		program: Program,
		debug: bool,
	) -> Mapping[str, int]:
	"""
	Computes the summary of each function. Takes into account possibles cross 
	dependency between functions by using the topological order of SCCs.
	"""
	
	summaries: Mapping[str, int] = {}
	cfgs: List[CFG] = program.get_cfgs()
	defined_functions: Mapping[str, bool] = program.get_defined_functions()

	# First, we need to define the order of computation and the relations 
	# between calls by using Tarjan's strongly connected components algorithm
	G = build_dependency_graph(cfgs) # converting CFGs in a suitable graph structure
	sccs = G.scc()					 # apply Tarjan's SCC algorithm on the graph
	
	if debug:
		print(sccs)

	# How to interpret SCCs?
	# If two functions are mutually calling themselves, they should be in the 
	# strongly connected component.
	# Thus, for computing functions summaries, we just need to compute the
	# summary of each function of each SCC following the reverse topological
	# order.
	# Please note: if there is more than one function in a SCC, we need to
	# perform the computation of function summaries until we meet a fixed-point.

	for scc in sccs:
		if len(scc) == 1: # no cross dependency between functions
			cfg: CFG = cfgs[scc[0]] # the only CFG of the component
			summaries = summarize(cfg, summaries, defined_functions)

		else: # there is more than one function in the SCC: cross dependencies
			local_summaries: Mapping[str, int] = {}
			new_local_summaries: Mapping[str, int] = {}

			while True : # looping until we meet a fixed-point
				for n in scc:
					cfg: CFG = cfgs[n]
					local_summaries[n] = summaries.get(cfg.get_name())
					summaries = summarize(cfg, summaries, defined_functions)
					new_local_summaries[n] = summaries.get(cfg.get_name())	

				if local_summaries == new_local_summaries: # fixed-point?
					break

	return summaries

def summarize(
		cfg: CFG,
		summaries: Mapping[str, int],
		defined_functions: Mapping[str, bool]
	) -> Mapping[str, int]:
	"""
	Computes the summary of a function (CFG) and stores it in the dictionnary
	"""

	heap: List[Tuple[int, int]] = []
	heapq.heapify(heap) # min-heap
	visited: List[bool] = [False] * (len(cfg.get_basic_blocks()))

	# Quick explanation: computing the summary of a function comes down to
	# computing the distance of the shortest path between the function's entry
	# point and the function's nearest exit point.
	# Therefore, we use Dijkstra's algorithm with a min-heap (priority queue)
	# where the priority is the distance between the first basic block and the
	# current basic block (where the distance is itself defined by the 
	# sum of the size of all basic blocks taken and all called function summaries)

	# Starting Dijkstra's algorithm with the first BB of the CFG in the worklist
	n: int = cfg.get_basic_block(0).get_id()
	last_instr: str = get_last_instr(cfg.get_basic_block(0))
	heapq.heappush(heap, 
				   (cfg.get_basic_block(0).size() + 
					call_cost(last_instr, summaries, defined_functions),
					n)
				  )
	visited[n] = True

	while heap:
		s = heapq.heappop(heap) # element with the hightest priority
		current_bb: BasicBlock = cfg.get_basic_block(s[1])
		last_instr = get_last_instr(current_bb)

		# have we reached the end of the CFG?
		if is_end_of_cfg(last_instr, current_bb):
			# end of Dijkstra's algorithm: we found the shortest path to exit
			# the function, hence the function's summary
			summaries[cfg.get_name()] = s[0]
			return summaries

		for n in current_bb.get_succ(): # looking for successors
			next_bb: BasicBlock = cfg.get_basic_block(n)
			if not visited[n]: # the shortest path to n has already been found
				last_instr = get_last_instr(next_bb)
				heapq.heappush(heap,
							   (s[0] +
		   						next_bb.size() +
								call_cost(last_instr, summaries, defined_functions),
								n)
							   )
				visited[n] = True

	# if all BB has been visited and yet no exit has been found: the summary of
	# the function is infinite
	summaries[cfg.get_name()] = math.inf
	return summaries

def call_cost(
		last_instr: str, 
		summaries: Mapping[str, int], 
		defined_functions: Mapping[str, bool]
	) -> int:
	"""
	Returns the cost of a potential call in a function summary (the called 
	function summary).
	If there is no call, or the called function is not defined in the LLVM file,
	then the cost is 0.
	"""
	call_value: int = 0

	if is_call(last_instr):
		# the current BB called a function: we have to add the summary of the
		# called function in the computation of the summary of the current CFG
		called_func: str = extract_called_function(last_instr)

		# checking if the summary has already been computed
		if summaries.get(called_func) != None:
			call_value = summaries.get(called_func)

		# checking if the function is defined in the LLVM file
		elif defined_functions.get(called_func) == None:
			call_value = 0	# we ignore the call of an undefined function 
		
		else: # no summary computed and defined function
			call_value = math.inf

	return call_value
