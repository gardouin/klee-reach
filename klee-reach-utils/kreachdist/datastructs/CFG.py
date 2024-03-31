from __future__ import annotations

from kreachdist.datastructs.BasicBlock import BasicBlock

from typing import List, Mapping

class CFG:
	"""
	A CFG is defined as a list of basic blocks.
	
	Some basic blocks contain a label: labels are used to identify the part of 
	the code we jump on when we follow a br instruction. Because some br 
	instructions refer to labels that are not yet seen in parsing, it is not 
	possible to represent the edges of the CFG in a single pass. That is why we 
	first construct a mapping table between the labels in the LLVM code and the 
	identifiers of the corresponding basic blocks. This table will be used in a 
	second step to build the edges.
	
	A CFG is identified by a unique identifier and name (both of which are 
	useful depending on how we want to identify it).
	"""
	def __init__(self: CFG, name: str, id: int) -> CFG:
		self.name: str = name
		self.id: int = id

		# ordered list of CFG's basic blocks
		self.basic_blocks: List[BasicBlock] = []

		# this list keep track of which label is associated with which BB
		# (labels[x] yields the id of the basic block containing label x)
		self.labels: Mapping[str, int] = {}


	def add_basic_block(self: CFG, basic_block: BasicBlock) -> None:
		"""
		Adds a BB in the CFG
		"""
		self.basic_blocks.append(basic_block)
		return None

	def get_basic_blocks(self: CFG) -> List[BasicBlock]:
		"""
		Returns the list of all BB
		"""
		return self.basic_blocks

	def get_basic_block(self: CFG, bb_id: int) -> BasicBlock:
		"""
		Returns the bb_id BB
		"""
		return self.basic_blocks[bb_id]

	def add_label(self: CFG, label: str, bb_id: int) -> None:
		"""
		Adds a label and is associated BB in labels
		"""
		self.labels[label] = bb_id
		return None

	def get_name(self: CFG) -> str:
		"""
		Gets CFG's name
		"""
		return self.name
	
	def get_id(self: CFG) -> int:
		"""
		Gets CFG's name
		"""
		return self.id

	def set_name(self: CFG, name: str) -> None:
		"""
		Sets the name of the CFG
		"""
		self.name = name
		return None

	def size(self: CFG) -> int:
		"""
		Gets the size of the CFG (i.e. the number of BB)
		"""
		return len(self.basic_blocks)

	def get_id_by_label(self: CFG, label: str) -> int:
		"""
		Gets the BB id containing the label 
		"""
		return self.labels.get(label)

	def display_content(self: CFG) -> None:
		"""
		Displays CFG's content
		"""
		print(f"Content of {self.name}'s Basics Blocks")
		for bb in self.basic_blocks:
			bb.display_content()
		return None
