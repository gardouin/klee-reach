from __future__ import annotations

class LLVMInstr:
	"""
	A LLVM instruction is represented by a structure containing an integer as 
	the line number of the instruction and a string as the content of the 
	instruction itself.
	"""

	def __init__(self: LLVMInstr, line_number: int, instr: str) -> LLVMInstr:
		self.line_number: int = line_number
		self.instr: str = instr

	def get_instr(self: LLVMInstr) -> str:
		"""
		Gets the instruction field of the LLVMInstr
		"""
		return self.instr

	def get_line(self: LLVMInstr) -> int:
		"""
		Gets the line_number field of the LLVMInstr
		"""
		return self.line_number
