from __future__ import annotations

from kreachdist.datastructs.CFG import CFG
from kreachdist.utils.regex import extract_called_function, is_call
from kreachdist.utils.misc import get_last_instr, get_cfg_by_name

from collections import defaultdict
from typing import List, Dict

# Note: the following class is adapted from:
# https://www.geeksforgeeks.org/tarjan-algorithm-find-strongly-connected-components/

class SCCGraph:
	"""
	This class represents a graph suitable for Tarjan's SCC algorithm
	"""
	def __init__(self: SCCGraph, n: int) -> SCCGraph:
		self.n: int = n
		self.graph: Dict[int, int] = defaultdict(list)
		self.t: int = 0

	def add_edge(self: SCCGraph, u: int, v: int) -> None:
		"""
		Adds an edge to the graph from u to v
		"""
		self.graph[u].append(v)
		return None

	def scc_util(
			self: SCCGraph,
			u: int,
			low: List[int],
			disc: List[int],
			stack_member: List[bool],
			st: List[int],
			sccs: List[List[int]]
		) -> None:
		
		disc[u] = self.t
		low[u] = self.t
		self.t += 1
		stack_member[u] = True
		st.append(u)

		for v in self.graph[u]:
			if disc[v] == -1:
				self.scc_util(v, low, disc, stack_member, st, sccs)
				low[u] = min(low[u], low[v])

			elif stack_member[v] == True:
				low[u] = min(low[u], disc[v])

		w = -1
		scc = []
		if low[u] == disc[u]:
			cnt = 0
			while w != u:
				w = st.pop()
				scc.append(w)
				if cnt > 1:
					print("WARNING: SCC found")
				stack_member[w] = False
				cnt += 1
			sccs.append(scc)

		return sccs

	def scc(self: SCCGraph) -> List[List[int]]:
		"""
		Performs Tarjan's algorithm and returns a list in a reverse topological 
		order
		"""
		disc = [-1] * self.n
		low = [-1] * self.n
		stack_member = [False] * self.n
		st = []
		sccs = []

		for i in range(self.n):
			if disc[i] == -1:
				sccs = self.scc_util(i, low, disc, stack_member, st, sccs)
		return sccs

# Util function for building the dependency graph from CFGs:

def build_dependency_graph(cfgs: List[CFG]) -> SCCGraph:
	"""
	Builds a dependency graph for calls between CFGs
	"""
	G: SCCGraph = SCCGraph(len(cfgs))
	i: int = 0
	for f in cfgs:
		for bb in f.get_basic_blocks():
			last_instr: str = get_last_instr(bb)
			if is_call(last_instr): # the BB ended with a call
				called_func: str = extract_called_function(last_instr)
				if get_cfg_by_name(cfgs, called_func) != None:
					G.add_edge(get_cfg_by_name(cfgs, f.name).get_id(),
							   get_cfg_by_name(cfgs, called_func).get_id())
		i += 1
	return G
