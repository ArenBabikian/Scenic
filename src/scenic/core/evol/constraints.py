
from enum import Enum

class Cstr_type(Enum):
	ONROAD = 0

	NOCOLLISION = 10

	CANSEE = 20

	HASTOLEFT = 30
	HASTORIGHT = 31
	HASBEHIND = 32
	HASINFRONT = 33

	DISTCLOSE = 40
	DISTMED = 41
	DISTFAR = 42

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