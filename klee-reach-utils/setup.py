from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'A library for computing .dist required by A-star KLEE\'s search heuristic'
LONG_DESCRIPTION = 'A library for computing a `.dist` file containing the distances between an LLVM instruction and a target instruction in the same LLVM file.'

setup(
	name="kreachdist", 
	version=VERSION,
	author="Guilhem Ardouin",
	author_email="guilhem.ardouin@enseirb-matmeca.fr",
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	packages=find_packages(),
	install_requires=[]
)
