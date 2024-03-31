from __future__ import annotations
import math
from typing import List

class DistanceContainer:
	"""
	This class represents the container of the distances between all instructions 
	and the target
	"""

	def __init__(self: DistanceContainer) -> DistanceContainer:
		self.data: List[str] = []

	def add_element(self: DistanceContainer, line: int, distance: int) -> None:
		"""
		Adds an element to the container
		"""
		if distance != math.inf:
			self.data.append(f"{line}:{distance}")
		return None

	def write_in_file(self, file_name):
		"""
		Outputs the container in a file (.dist)
		"""
		f = open(file_name + ".dist", 'w')
		for line in self.data:
			f.write(line + "\n")
		f.close()
		return None

	def display(self: DistanceContainer) -> None:
		"""
		Displays the container
		"""
		for e in self.data:
			print(e)
		return None
