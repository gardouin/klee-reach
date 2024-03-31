from kreachdist.compute_distance import build_dist_file
from kreachdist.summary import summarize_functions
from kreachdist.parse import parse, display_result

import sys

def compute_distance():
	"""
	Executes the distance computation and outputs the result in a .dist file
	"""

	#########################
	# PARSING THE LLVM FILE #
	#########################
	if len(sys.argv) < 2:
		print(f"ERROR: LLVM file missing")
		return None
	debug = (len(sys.argv) > 2) and (sys.argv[2] == "debug")

	file_name_path = sys.argv[1]

	program = parse(file_name_path)

	if debug:
		display_result(program.get_cfgs())

	#######################
	# COMPUTING SUMMARIES #
	#######################
	summaries = summarize_functions(program, debug)

	if debug:
		print(summaries)
	
	#######################
	# COMPUTING DISTANCES #
	#######################
	dist = build_dist_file(program.get_cfgs(), summaries, debug)

	################################
	# WRITTING DISTANCES IN A FILE #
	################################
	file_name_path = file_name_path[:-3]
	dist.write_in_file(file_name_path)
	
	print(f"Distances wrote in {file_name_path}.dist")

	return None

def main():
	compute_distance()

main()
