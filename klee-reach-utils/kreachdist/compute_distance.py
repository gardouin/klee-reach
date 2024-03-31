from kreachdist.datastructs.BasicBlock import BasicBlock
from kreachdist.datastructs.DistanceContainer import DistanceContainer
from kreachdist.datastructs.CFG import CFG
from kreachdist.utils.CallPaths import compute_g_call, compute_g_ret, transpose_g_call, transpose_g_ret
from kreachdist.utils.regex import is_klee_reach, extract_called_function, is_label_definition, is_define, is_call
from kreachdist.utils.misc import get_cfg_by_name, get_last_instr


import heapq
from typing import Mapping, List, Tuple

def build_dist_file(
		cfgs: List[CFG],
		summaries: Mapping[str, int],
		debug: bool
	) -> DistanceContainer:
	"""
	Compute all distances between LLVM instructions to the LLVM target instruction
	"""

	# Computing G_call & G_ret from CFGs
	g_call: Mapping[Tuple[str, int], Tuple[str, int]] = compute_g_call(cfgs)
	g_ret: Mapping[Tuple[str, int], List[Tuple[str, int]]] = compute_g_ret(cfgs, g_call)
	
	# Transpose G_call & G_ret (we only work on tranpose graph here)
	g_call_t: Mapping[Tuple[str, int], List[Tuple[str, int]]] = transpose_g_call(g_call)
	g_ret_t: Mapping[Tuple[str, int], List[Tuple[str, int]]] = transpose_g_ret(g_ret)

	dist: DistanceContainer = DistanceContainer()

	target_func: str
	target_bb_id: int
	target_func, target_bb_id = find_target(cfgs)

	if target_func == "": # no target found (i.e. no 'klee-reach' instruction)
		print("WARNING: no target found")
		return dist

	heap: List[int, Tuple[str, int, bool]]= []
	heapq.heapify(heap) # min-heap
	current_cfg: CFG = get_cfg_by_name(cfgs, target_func)

	# (distance, (cfg_name, basic_block_id, has_took_ret))
	heapq.heappush(heap,
				   (current_cfg.get_basic_block(target_bb_id).size(),
					(target_func, target_bb_id, False)
				   )
				  )
	visited: List[List[bool]] = [[False for _ in cfg.get_basic_blocks()] for cfg in cfgs]

	if debug:
		print("Starting distance computation...")

	# Please note: we work with the tranpose representation of CFGs

	while heap:
		s = heapq.heappop(heap)

		if debug:
			print(f"-> {s}")

		current_cfg: CFG = get_cfg_by_name(cfgs, s[1][0])
		current_bb: BasicBlock = current_cfg.get_basic_block(s[1][1])

		dist_value: int = s[0]
		# assigning a distance for each instr in the basic block according to 
		# dist_value
		for line in current_bb.get_llvm_instructions():
			# we only attribuate a distance for instructions executed by KLEE
			if not is_label_definition(line.get_instr()) and not is_define(line.get_instr()):
				dist_value -= 1
				dist.add_element(line.get_line(), dist_value)

		current_cfg_id: int = current_cfg.get_id()
		current_cfg_name: str = current_cfg.get_name()
		current_dist: int = s[0]
		has_took_ret: bool = s[1][2]

		# finding next basic blocks within the current CFG
		for next_bb_id in current_bb.get_pred(): # compute the dist for each next BB
			if not visited[current_cfg_id][next_bb_id]:
				# if the next BB called a func, we need to add the function
				# summary in value
				summary = add_summary(summaries,
						  			  current_cfg.get_basic_block(next_bb_id))
				next_bb_size: int = current_cfg.get_basic_block(next_bb_id).size()
				value = current_dist + next_bb_size + summary

				heapq.heappush(heap,
				   			   (value, (current_cfg_name, next_bb_id, has_took_ret))
							  )

				visited[current_cfg_id][next_bb_id] = True

		# Following operations involve finding possible destinations
		# (other CFGs) by following call or return paths
		# Please note: when a ret path is taken, it is not possible anymore to 
		#              take "call path" anymore
	
		# ret paths
		heap, visited = take_call_path("ret",
								 		cfgs,
										g_ret_t, # using (G_ret)^T
										current_cfg,
										current_bb,
										visited,
										heap,
										current_dist,
										has_took_ret
									  )

		# call paths
		heap, visited = take_call_path("call",
								 		cfgs,
										g_call_t, # using (G_call)^T
										current_cfg,
										current_bb,
										visited,
										heap,
										current_dist,
										has_took_ret
									  )

	return dist

def find_target(cfgs: List[CFG]) -> Tuple[str, int]:
	"""
	Returns the name of the CFG and the id of the BB containing the first call 
	to klee_reach (if exists)
	"""
	for cfg in cfgs:
		for bb in cfg.get_basic_blocks():
			last_llvm_instr: str = get_last_instr(bb)
			if is_klee_reach(last_llvm_instr):
				return cfg.get_name(), bb.get_id()

	return "", -1 # no target found

def add_summary(
		summaries: Mapping[str, int],
		target_bb: BasicBlock
	) -> int:
	"""
	Returns the potential value of a function summary (if this value exists)
	"""
	last_instr: str = get_last_instr(target_bb)
	if is_call(last_instr):
		called_func: str = extract_called_function(last_instr)
		summary: int | None = summaries.get(called_func)
		if summary != None:
			return summary
	return 0 # undefined summaries are considered null

def take_call_path(
		path: str,
		cfgs: List[CFG],
		graph: Mapping[Tuple[str, int], List[Tuple[str, int]]],
		current_cfg: CFG,
		current_bb: BasicBlock,
		visited: List[List[bool]],
		heap: List[Tuple[int ,Tuple[str, int]]],
		v: int,
		has_took_ret: bool
	) -> Tuple[List[Tuple[int ,Tuple[str, int]]], List[List[bool]]]:

	# getting possible destinations from current position to others CFGs
	next_callret_list: List[Tuple[str, int]] = graph.get((current_cfg.get_name(), 
													   current_bb.get_id()))

	# we can't take a "call" edge when a ret one was previously taken
	if has_took_ret and path == "call":
		return heap, visited

	if next_callret_list != None:
		for next_callret in next_callret_list:
			next_cfg_name: str = next_callret[0]
			next_cfg: CFG = get_cfg_by_name(cfgs, next_cfg_name)
			next_cfg_id: int = next_cfg.get_id()
			next_bb = next_callret[1]

			if not visited[next_cfg_id][next_bb]:
				next_bb_size: int = cfgs[next_cfg_id].get_basic_block(next_bb).size()
				value = v + next_bb_size

				if has_took_ret or path == "ret":
					new_took_ret = True
				else:
					new_took_ret = False

				heapq.heappush(heap,
				   			   (value, ((next_cfg_name), next_bb, new_took_ret)))
				visited[next_cfg_id][next_bb] = True

	return heap, visited
