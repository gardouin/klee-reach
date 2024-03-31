from __future__ import annotations

from kreachdist.datastructs.CFG import CFG

from typing import List, Mapping

class Program:
	"""
	This class represents all CFGs and an additional information about the 
	program: these are the function defined in the LLVM file
	"""
	def __init__(self: Program) -> Program:
		self.cfgs: List[CFG] = []

		# All functions that are defined in the LLVM file
		self.defined_functions: Mapping[str, bool] = {}

	def add_cfg(self: Program, cfg: CFG) -> None:
		"""
		Adds a CFG to the list of CFGs
		"""
		self.cfgs.append(cfg)
		return None

	def get_cfgs(self: Program) -> List[CFG]:
		"""
		Gets all program's CFGs
		"""
		return self.cfgs

	def add_defined_function(self: Program, function_name: str) -> None:
		"""
		Takes a defined function into account
		"""
		self.defined_functions[function_name] = True
		return None

	def get_defined_functions(self: Program) -> Mapping[str, bool]:
		"""
		Gets all program's defined functions
		"""
		return self.defined_functions
