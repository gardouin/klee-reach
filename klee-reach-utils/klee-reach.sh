#!/usr/bin/env bash

##########################################
#           USER CONFIGURATION           #
########################################## 

# Path to KLEE executable (built with ASTAR module)
klee=""
# Specify absolute path to klee-reach-utils
kreachdist="."

if [ "$klee" = "" ]
then
	echo "ERROR: path to KLEE executable not specified."
	exit
fi

##########################################
#             SCRIPT OPTIONS             #
########################################## 

OPTSTRING=":hvaAk"

verbose=0
astar=0
astar2=0
kleesearch=0

while getopts ${OPTSTRING} opt; do
	case ${opt} in
	h)
		echo "=== KLEE-REACH : HELP ==="
		echo ""
		echo "Options:"
		echo "Selecting the search heuristic:"
		echo "  -a : using A-star searcher"
		echo "  -A : using A-star2 searcher (guiding the exploration towards the Unknown)"
		echo "  -k : using KLEE default searcher"
		echo "Debugging:"
		echo "  -v : verbose mode"
		exit
		;;
	v)
		verbose=1
		;;
	a)
		astar=1
		astar2=0
		kleesearch=0
		;;
	A)
		astar=0
		astar2=1
		kleesearch=0
		;;
	k)
		astar=0
		astar2=0
		kleesearch=1
		;;
	?)
		if [ $OPTARG = "-" ]; then # end of script options
			break
		else
			echo "Invalid option: -$OPTARG (see ./klee-reach -h)"
			exit 1
		fi
		;;
	esac
done

if [ $kleesearch -ne 1 ]
	then
	if [ $astar -eq 0 ]
	then
		if [ $astar2 -eq 0 ]
		then
			echo "WARNING: No search heuristic specified: using A-star2 (default)"
			echo "         (to choose the search heuristic, please refer to ./klee-reach.sh -h)"
			echo ""
			astar2=1
		else
			echo "Selected search heuristic: A-star2"
		fi
	else
		echo "Selected search heuristic: A-star"
	fi
fi

##########################################
#          COLLECTING ARGUMENTS          #
##########################################

args=""
bc=0			# bytecode file?
bc_file=""		# bytecode filename

script_opt='^-[aAkv]' # regex for script options (getopts) 
is_max_instr='^--max-instructions='
is_output_dir='^--output-dir='
max_instr=""
output_dir=""

# note: we have to the same order for running KLEE
for arg in $@
do
	if [ $bc -eq 0 ]
	then
		# checking file extension
		extension=$(echo $arg | sed 's/.*\.//')
		if [ "$extension" = "bc" ]
		then
			# bytecode file found
			bc=1
			bc_file=$arg
		fi
	fi
	if ! [[ $arg =~ $script_opt ]] # we don't want to get script option in args
	then
		if [[ $arg =~ $is_max_instr ]] # special case: we can't use twice this argument in KLEE
		then
			max_instr=$arg
		elif [[ $arg =~ $is_output_dir ]] # same case with --output-dir
		then
			output_dir=$arg
		else
			args="$args $arg"
		fi
	fi
done

if [ $bc -eq 0 ]
then
	echo "ERROR: no bitcode file (.bc) found"
	exit
fi

echo $bc_file
filename=$(echo $bc_file | sed 's#.*/##; s#[.][^.]*$##') # sed -r "s/.+\/(.+)\..+/\1/")

##########################################
#     GENERATING LLVM FILE WITH KLEE     #
##########################################

### Cleaning potential error files
if [ $verbose -eq 1 ]
then
	echo "Cleaning potential error files..."
	echo "  rm -f __klee_dist_output__"
	echo "  rm -f __compute_dist_output__"
	echo "  > Done"
fi
rm -f __klee_dist_output__
rm -f __compute_dist_output__

# note: using same arguments ensures the generation of the "correct" LLVM file

echo "Generating LLVM file..."

### Using klee to generate the LLVM file (we use a temporary output directory)
if [ $verbose -eq 1 ]
then
	echo "  $klee --max-instructions=1 --output-dir="__klee_dist_dir__" $args 2&> __klee_dist_output__"
fi
$klee --max-instructions=1 --output-dir="__klee_dist_dir__" $args 2&> __klee_dist_output__

### Checking if the last command exits on a success
if [ $? -ne 0 ]
then
	echo "ERROR: an error has occured."
	cat __klee_dist_output__
	exit
fi

### Adding potential --max-instructions option
args="$max_instr$output_dir$args"

### Getting LLVM file
if [ $verbose -eq 1 ]
then
	echo "  mv __klee_dist_dir__/assembly.ll $filename.ll"
fi
mv __klee_dist_dir__/assembly.ll $filename.ll

### Cleaning temporary files
if [ $verbose -eq 1 ]
then
	echo "  rm -f __klee_dist_output__"
	echo "  rm -rf __klee_dist_dir__"   
fi
rm -f __klee_dist_output__
rm -rf __klee_dist_dir__

echo "  > Done"

#########################################
#    COMPUTING DISTANCE WITH PYTHON     #
#########################################

echo "Computing distances..."
if [ $verbose -eq 1 ]
then
	echo "  python3 $kreachdist/kreachdist/main.py $filename.ll > __compute_dist_output__"   
fi
python3 $kreachdist/kreachdist/main.py $filename.ll > __compute_dist_output__
if [ $? -ne 0 ]
then
	echo "ERROR: an error has occured."
	exit
fi

### Cleaning temporary file
if [ $verbose -eq 1 ]
then
	echo "  rm -f __compute_dist_output__"
fi
rm -f __compute_dist_output__

echo "  > Done"

#########################################
#        RUNNING KLEE WITH ASTAR        #
#########################################

selected="KLEE heuristic"
searcher=""
if [ $astar -eq 1 ]
then
	selected="A-star"
	searcher="--search=astar"
elif [ $astar2 -eq 1 ]
then
	selected="A-star2"
	searcher="--search=astar2"
fi

echo ""
echo "Starting KLEE with $selected..."

if [ $verbose -eq 1 ]
then
	echo "  $klee --exit-on-error-type=Reach --input-distance-file=$filename.dist $searcher $args"
fi
echo ""

$klee --exit-on-error-type=Reach --input-distance-file=$filename.dist $searcher $args
