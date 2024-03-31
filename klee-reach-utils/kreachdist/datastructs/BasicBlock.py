from __future__ import annotations

from kreachdist.datastructs.LLVMInstr import LLVMInstr

from typing import List

class BasicBlock:
	"""
	A basic block is defined as a straight-line code sequence where the last 
	instruction is either : 
	- a LLVM terminator instruction
			(see: https://llvm.org/docs/LangRef.html#terminator-instructions)
	-  or a call to a *defined* function in the LLVM file
	The representation of the basic block includes a list of all LLVM instructions 
	within it.

	The relationships between basic blocks, i.e. the edges of the CFG, are 
	represented by a list of successors for each basic block. For convenience, a 
	list of predecessors is also maintained.

	Each basic block is identified by a unique identifier, starting at $0$ and 
	incremented for each new basic block
	"""

	def __init__(self: BasicBlock, id: int) -> BasicBlock:
		self.id: int = id

		# ordered list of the basic block LLVM's instructions
		self.llvm_instructions: List[LLVMInstr] = []

		self.succ: List[int] = []

		self.pred: List[int] = []

		# number of ignored instructions (i.e. LLVM lines that are ignored by 
		# KLEE but collected in llvm_instructions for debugging purpose)
		self.ignored_instructions: int = 0

	def get_id(self: BasicBlock) -> int:
		"""
		Returns the BB's id
		"""
		return self.id

	def add_llvm_instr(self: BasicBlock, llvm_instr: LLVMInstr) -> None:
		"""
		Adds a new LLVM instruction in the BB
		"""
		self.llvm_instructions.append(llvm_instr)
		return None

	def get_llvm_instructions(self: BasicBlock) -> List[LLVMInstr]:
		"""
		Returns all LLVMInstr of the BB
		"""
		return self.llvm_instructions

	def get_llvm_instr(self: BasicBlock, instr_id: int) -> LLVMInstr:
		"""
		Returns the LLVMInstr at instr_id
		"""
		return self.llvm_instructions[instr_id]

	def get_instr(self: BasicBlock, instr_id: int) -> str:
		"""
		Returns LLVMInstr's instruction (content) at instr_id
		"""
		return self.llvm_instructions[instr_id].get_instr()

	def get_instr_line(self: BasicBlock, instr_id: int) -> int:
		"""
		Returns LLVMInstr's line at instr_id
		"""
		return self.llvm_instructions[instr_id].get_instr()

	def add_succ(self: BasicBlock, id: int) -> None:
		"""
		Adds a new successor for the BB
		"""
		self.succ.append(id)
		return None

	def get_succ(self: BasicBlock) -> List[int]:
		"""
		Gets the BB successors list
		"""
		return self.succ

	def reset_succ(self: BasicBlock) -> None:
		"""
		Clear the BB successors list
		"""
		self.succ = []
		return None

	def add_pred(self: BasicBlock, id: int) -> None:
		"""
		Adds a new predecessor for the BB 
		"""
		self.pred.append(id)
		return None

	def get_pred(self: BasicBlock) -> None:
		"""
		Gets the BB predecessors list
		"""
		return self.pred

	def len(self: BasicBlock) -> int:
		"""
		Gets BB's length (i.e. the number of LLVM instructions)
		"""
		return len(self.llvm_instructions)

	def size(self: BasicBlock) -> int:
		"""
		Gets BB's size (i.e. the number of EXECUTED [by KLEE] LLVM instructions)
		"""
		return len(self.llvm_instructions) - self.ignored_instructions

	def new_ignored_instruction(self: BasicBlock) -> None:
		"""
		Increments ignored_instructions

		An ignored instruction is a LLVM line that is ignored by KLEE but 
		collected in the basic block for debugging purpose
		"""
		self.ignored_instructions += 1
		return None

	def display_content(self: BasicBlock) -> None:
		"""
		Displays BB's content
		"""
		print(f"Content of BasicBlock #{self.id} (size = {self.size()})")
		for llvm_instr in self.llvm_instructions:
			print((llvm_instr.get_line(), llvm_instr.get_instr()))
		print(f"Successors: {self.succ}")
		print(f"Predecessors: {self.pred}")
		return None
