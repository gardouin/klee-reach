from kreachdist.datastructs.BasicBlock import BasicBlock
from kreachdist.datastructs.CFG import CFG
from kreachdist.datastructs.Program import Program
from kreachdist.datastructs.LLVMInstr import LLVMInstr
from kreachdist.utils.regex import is_end_of_define, is_define, extract_called_function, is_switch, is_switch_end, is_label_definition, extract_label_from_def, search_label_in_cond_br, is_uncond_br, extract_label, is_call, is_br, has_label
from kreachdist.utils.misc import new_id, is_ret, get_last_instr, reset_last_bb_succ, is_end_of_bb

import re
from typing import List, Tuple, Match, Union

###
### TODO - generalize br/switch statements
###
def parse(file_name: str) -> Program:
	"""
	Parses a LLVM file and breaks it into basic blocks grouped into CFGs
	Outputs it as a 'Program', which a structure representing all information about
	the LLVM file
	"""
	program: Program = Program()
	file = open(file_name, "r")
	lines: List[str] = file.readlines()
	line_number: int = 0
	cfg: CFG = CFG("", -1)
	bb: BasicBlock = BasicBlock(new_id(-1))
	wait_for_switch_end: bool = False # switch management

	# we iterate over each line...
	for line in lines:
		line_number += 1
		
		# we don't take empty line into account
		if line != "\n":
			# 2 cases:
			#   1. The line is the end of a function ('}' instruction)
			#   2. The line is another instruction

			if is_end_of_define(line):
				# end of a function => end of the current basic block
				# meaning the BB has no direct successor
				# thus we delete the potential direct sucessor:
				reset_last_bb_succ(cfg)
				# end of a function => end of the CFG
				# thus we add the current CFG to the Program container
				program.add_cfg(cfg) # note: next CFG will be setup when define
									 #       statement reached

			else:

				# is the LLVM line a label definition?
				if (is_label_definition(line)):
					label: str = extract_label_from_def(line)
					cfg.add_label(label, bb.id)
					# a label definition is not interpreted as an instruction
					# by KLEE, thus we don't want to count it into the total 
					# number of instructions in the BB (that we'll use in the
					# computation of the distance):
					bb.new_ignored_instruction()

				# is the LLVM line a define statement?
				if is_define(line):
					# a "define" statement marks the beggining of a new CFG
					# (consequently of a new BB too)
					name: str = extract_called_function(line)
					program.add_defined_function(name) # we maintain the list of
													   # all defined function
					cfg = CFG(name, cfg.id + 1) # defining the new CFG
					bb = BasicBlock(new_id(-1)) # defining the new BB
					bb.new_ignored_instruction() # define is not an instruction

				# note: even if the line is a label definition or a define
				#       statement, we add it to the BB for debugging purpose
				# 		we only need the number of 'non-instruction': BB's 
				#       ignored_instructions variable keep tracks of that)

				# adding the instruction to the current BB
				bb.add_llvm_instr(LLVMInstr(line_number, line))

				##############################
				## handling BB's termination #
				##############################

				# A BB ends either with a terminator instruction (see below) or 
				# a call to a defined function

				if is_switch(line):
					wait_for_switch_end = True # we need to collect all labels
											   # before ending the BB

				# we continue with the current BB until we meet the end of the
				# switch statement
				if wait_for_switch_end and is_switch_end(line):
					wait_for_switch_end = False
					# we can't add successors and predecessors until we resolved
					# all labels: thus, we set `add_pred` to False	
					cfg, bb = next_basic_block(cfg, bb, False)

				elif is_br(line):
					# we can't add successors and predecessors until we resolved
					# all labels: thus, we set `add_pred` to False
					cfg, bb = next_basic_block(cfg, bb, False)

				# `is_end_of_bb` checks whether the instruction is a terminator
				# instruction
				# see: https://llvm.org/docs/LangRef.html#terminator-instructions
				# there exits two kind of these intructions:
				#   - with jumps to labels,
				#   - and without jump

				# is the instruction either a call, ret or terminator instr
				# without jump?
				elif is_call(line) or is_ret(line) or is_end_of_bb(line, False):
					# we add a direct successor (thus we set `add_pred` to True
					# for adding a direct predecessor)
					bb.add_succ(bb.id + 1)
					cfg, bb = next_basic_block(cfg, bb, True)

				# is the instruction a terminator instr with jumps?
				elif is_end_of_bb(line, True):
					# todo: handle that...
					print(f"WARNING: terminator instruction currently not "
		   				   "supported: {line}")
					# we can't add successors and predecessors until we resolved
					# all labels: thus, we set `add_pred` to False
					cfg, bb = next_basic_block(cfg, bb, False)

	file.close()

	# we need another pass to assign successors and predecessors for br/switch
	# (we call them 'indirect' successors/predecessors)
	add_indirect_succ_pred(program.get_cfgs())

	return program

def next_basic_block(
		control_flow_graph: CFG,
		basic_block: BasicBlock,
		add_pred: bool
	) -> Tuple[CFG, BasicBlock]:
	"""
	Updates the current CFG with the current BB and replaces the current BB with
	a fresh BB
	"""
	control_flow_graph.add_basic_block(basic_block)

	# setting up a new BB
	basic_block = BasicBlock(new_id(basic_block.id)) # new_id increments
													 # basic_block.id

	# is the former BB a predecessor of the new BB?
	if add_pred:
		basic_block.add_pred(basic_block.id - 1)

	return control_flow_graph, basic_block

###
### TODO - handle remaining br statements in some terminator instructions...
### -> indirectbr, invoke, callbr, catchswitch, catchret, cleanupret
###

def add_indirect_succ_pred(cfgs: List[CFG]) -> None:
	"""
	Browses all CFGs looking up for jumps (br, switch, ... statements) and adds
	indirect successor and predecessor for BBs in a CFG when found
	"""
	for cfg in cfgs:

		# if a CFG contains at least a BB with a label...
		if (len(cfg.labels) > 0):

			for bb in cfg.get_basic_blocks():
				last_instr: str = get_last_instr(bb) # only the last instruction
													 # can contain a jump
													 # instruction

				# is the last instruction a 'br'?
				if is_br(last_instr):

					# if the last instruction is a br, there exists two kinds 
					# of br:
					#   - conditionals (=> two succ)
					#   - unconditionals (=> one succ)
					uncond_br: Union[Match[str], None] = is_uncond_br(last_instr)
					if uncond_br:
						label = extract_label(uncond_br.group())
						bb_id = cfg.get_id_by_label(label)
						bb.add_succ(bb_id)
						cfg.get_basic_block(bb_id).add_pred(bb.id)
					else: # cond_br
						labels = search_label_in_cond_br(last_instr)
						l1, l2 = labels
						l1 = extract_label(l1)
						l2 = extract_label(l2)
						bb1_id = cfg.get_id_by_label(l1)
						bb2_id = cfg.get_id_by_label(l2)
						bb.add_succ(bb1_id)
						cfg.get_basic_block(bb1_id).add_pred(bb.id)
						bb.add_succ(bb2_id)
						cfg.get_basic_block(bb2_id).add_pred(bb.id)
				
				# not a br statement: we could have a switch statement
				else:
					if is_switch_end(last_instr): # possible switch statement
						i, is_switch_instr, switch_instr = bb.len() - 1, False, []
						while i >= 0 and not is_switch_instr:
							switch_instr.append(bb.get_instr(i))
							is_switch_instr = is_switch(bb.get_instr(i))
							i -=1
						if is_switch_instr: # now, we are sure that it was a switch
							for line in switch_instr:
								label = has_label(line)
								if label:
									label = extract_label(label.group())
									bb_id = cfg.get_id_by_label(label)
									bb.add_succ(bb_id)
									cfg.get_basic_block(bb_id).add_pred(bb.id)

	return None

def display_result(cfgs: List[CFG]) -> None:
	"""
	Displays the content of basic blocks in all CFGs
	"""
	for cfg in cfgs:
		if (cfg.get_basic_blocks() != []):
			cfg.display_content()
	return None
