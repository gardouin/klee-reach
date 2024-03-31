from kreachdist.datastructs.BasicBlock import BasicBlock
from kreachdist.datastructs.CFG import CFG
from kreachdist.datastructs.LLVMInstr import LLVMInstr
from kreachdist.utils.regex import is_ret

import re
from typing import List, Union

def is_end_of_cfg(instr: str, basic_block: BasicBlock) -> bool:
	"""
	Checks if instr or basic_block is an exit point of the function
	"""
	return is_ret(instr) or basic_block.get_succ() == []

def new_id(current_id: int) -> int:
	"""
	Returns current_id + 1
	"""
	return current_id + 1

def get_cfg_by_name(cfgs: List[CFG], cfg_name: str) -> Union[CFG, None]:
	"""
	Returns the CFG cfg_name
	"""
	for cfg in cfgs:
		if cfg.get_name() == cfg_name:
			return cfg
	return None

def get_last_llvm_instr(basic_block: BasicBlock) -> LLVMInstr:
	"""
	Returns the last LLVM instruction of basic_block
	"""
	return basic_block.get_llvm_instr(-1)

def get_last_instr(basic_block: BasicBlock) -> str:
	"""
	Returns the last instruction of basic_block
	"""
	return get_last_llvm_instr(basic_block).get_instr()

def reset_last_bb_succ(cfg: CFG) -> None:
	"""
	Resets the list of successors for the last basic block of cfg 
	"""
	cfg.get_basic_block(-1).reset_succ()
	return None

###
### HANDLE SPECIALS LLVM KEYWORDS
###

## All terminator instructions (except ret, br & switch)
### Reference: https://llvm.org/docs/LangRef.html#terminator-instructions

### List of all terminator instructions with no label
terminator_instructions_no_label = ["resume ", "unreachable"]

### List of all terminator instructions with labels
terminator_instructions_with_label = [
	"indirectbr ", "invoke ", "callbr ", "catchswitch ", "catchret ",
	"cleanupret "
]

def is_end_of_bb(instr: str, with_label: bool) -> bool:
	"""
	Checks instr is a last instruction of a basic block
	"""
	terminator_instructions = terminator_instructions_with_label if with_label else terminator_instructions_no_label
	for keyword in terminator_instructions:
		if re.search(keyword, instr) != None:
			return True
	return False
