import re
from typing import Union, Match, List

### General LLVM

#### Functions

def is_define(instr: str) -> bool:
	"""
	Checks if instr is a define instruction 
	"""
	return re.search("define ", instr) != None

def is_end_of_define(instr: str) -> bool:
	"""
	Checks if instr is the end of a define instruction 
	"""
	return instr == "}\n"

def is_call(instr: str) -> bool:
	"""
	Checks if instr is a call to a function (excepts for llvm debug functions)
	"""
	return (re.search("call ", instr) != None) and (not is_llvm_debug_call(instr))

def is_llvm_debug_call(instr: str) -> bool:
	"""
	Checks if instr is a LLVM debug function
	"""
	return re.search("@llvm.dbg", instr) != None

def is_ret(instr: str) -> bool:
	"""
	Checks if instr is a return instruction 
	"""
	return re.search("ret ", instr) != None

def is_klee_reach(instr: str) -> bool:
	"""
	Checks if instr contains a reference to klee_reach()
	"""
	return re.search("@klee_reach()", instr) != None

def extract_called_function(instr: str) -> str:
	"""
	Extracts the name of the called function in instr

	Expected input: "call [type] @FUNC_NAME"
	Expected output: "@FUNC_NAME"
	"""
	called_func = re.search("@\w+", instr)
	return (called_func.group() if called_func != None else "")

#### Branches

def is_br(instr: str) -> bool:
	"""
	Checks if instr is a br instruction
	"""
	return re.search("br ", instr) != None

def is_switch(instr: str) -> bool:
	"""
	Checks if instr is a switch instruction
	"""
	return re.search("switch ", instr) != None

def is_switch_end(instr: str) -> bool:
	"""
	Checks if instr is the end of a switch statement (should be use in the 
	context	of a previous switch declaration)
	"""
	return re.search(" ]", instr) != None

def is_uncond_br(instr: str) -> Union[Match[str], None]:
	"""
	Checks if a br instruction is an unconditional one
	"""
	return re.search("br label (%([-a-zA-Z$._][-a-zA-Z$._0-9]*)|%([0-9]*))", instr);

#### LABELS
##### About labels: there are LLVM identifiers
##### LLVM standards: https://llvm.org/docs/LangRef.html#identifiers

def is_label_definition(line: str) -> bool:
	"""
	Checks whether the line is a label definition or not
	"""
	return ((re.search("([-a-zA-Z$._][-a-zA-Z$._0-9]*)|([0-9]*):", line) != None) 
			and (re.search("; preds =", line) != None))

def has_label(instr: str) -> bool:
	"""
	Checks if instr has a label inside
	"""
	return re.search("label %\d+", instr)

def extract_label(instr: str) -> str:
	"""
	Returns a label's name from a pre-formated string

	Expected input: "\w+ %LABEL_NAME \w+"
	Expected output: "LABEL_NAME"
	"""
	return (re.search("%([-a-zA-Z$._][-a-zA-Z$._0-9]*)|%([0-9]*)", instr).group())[1:]

def extract_label_from_def(instr: str) -> str:
	"""
	Returns a label's name from its definition in LLVM
	
	Expected input: "%LABEL_NAME:      ; pred %..."
	Expected output: "LABEL_NAME"
	"""
	return (re.search("([-a-zA-Z$._][-a-zA-Z$._0-9]*):|([0-9]*):", instr)).group()[:-1]

def search_label_in_cond_br(instr: str) -> List[str]:
	"""
	Returns an array of 2 strings

	Expected input: "br %COND, label %L1_NAME, label %L2_NAME"
	Expected output: [', label %L1_NAME', ', label %L2_NAME']
	"""
	return re.findall(", label %[-a-zA-Z$._][-a-zA-Z$._0-9]*|, label %[0-9]*", instr)
