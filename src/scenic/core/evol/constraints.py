
from enum import Enum

class Cstr_type(Enum):
	ONROAD = 1
	NOCOLLISION = 2
	CANSEE = 3
	# TODO Add CANNOTSEE

	HASTOLEFT = 4
	HASTORIGHT = 5
	HASBEHIND = 6
	HASINFRONT = 7

	DISTCLOSE = 8
	DISTMED = 9
	DISTFAR = 10

class Cstr():
	def __init__(self, t, src, tgt):
		self.type = t
		self.src = src
		self.tgt = tgt

	def pretty(self):
		return f'{self.type.name} : [{self.src}, {self.tgt}];'

	def __str__(self):
		return self.pretty()
	
	def __repr__(self):
		return self.pretty()