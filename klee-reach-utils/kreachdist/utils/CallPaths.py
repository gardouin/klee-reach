from kreachdist.datastructs.CFG import CFG
from kreachdist.utils.regex import extract_called_function, is_call
from kreachdist.utils.misc import get_last_instr, is_ret, get_cfg_by_name

from typing import Mapping, Tuple, List

def compute_g_call(cfgs: List[CFG]) -> Mapping[Tuple[str, int], Tuple[str, int]]:
	"""
	Computes G_call, an association table which associates each basic block b 
	from CFG c when b ends with a call to c' 
	"""
	g_call = {}
	for cfg in cfgs:
		for bb in cfg.get_basic_blocks():
			last_instr = get_last_instr(bb)
			if is_call(last_instr):
				func_called = extract_called_function(last_instr)
				g_call[(cfg.get_name(), bb.get_id())] = (func_called, 0)

	return g_call

def compute_g_ret(
		cfgs: List[CFG],
		g_call: Mapping[Tuple[str, int], Tuple[str, int]]
	) -> Mapping[Tuple[str, int], List[Tuple[str, int]]]:
	"""
	Computes G_ret, an association table which associates each CFG c and a basic 
	block b in G_call with all possible basic block b'+1 in c' where b' is a ret 
	instruction
	"""
	g_ret = {}
	for key in g_call:
		caller = key[0] 		# finding in G_call who call (CFG name)
		caller_bb = key[1]
		called_func = g_call[key][0] # called function (CFG name)
		target_cfg = get_cfg_by_name(cfgs, called_func) # getting the CFG
		if target_cfg != None: # some called function are not CFGs (klee_reach...)
			for bb in cfgs[target_cfg.get_id()].get_basic_blocks():
				last_instr = get_last_instr(bb)
				if is_ret(last_instr):
					if g_ret.get((called_func, bb.get_id())) == None:
						g_ret[(called_func, bb.get_id())] = []
					g_ret[(called_func, bb.get_id())].append((caller, caller_bb + 1))

	return g_ret

def transpose_g_call(
		g_call: Mapping[Tuple[str, int], Tuple[str, int]]
	) -> Mapping[Tuple[str, int], List[Tuple[str, int]]]:
	"""
	Computes the transpose graph of G_call	
	"""
	g_call_t = {}
	for key in g_call:
		if g_call_t.get(g_call.get(key)) == None:
			g_call_t[g_call.get(key)] = [key]
		else:
			g_call_t[g_call.get(key)].append(key)
	return g_call_t

def transpose_g_ret(
		g_ret: Mapping[Tuple[str, int], List[Tuple[str, int]]]
	) -> Mapping[Tuple[str, int], List[Tuple[str, int]]]:
	"""
	Computes the transpose graph of G_ret
	"""
	g_ret_t = {}
	for key in g_ret:
		for e in g_ret.get(key):
			g_ret_t[e] = [key]

	return g_ret_t
