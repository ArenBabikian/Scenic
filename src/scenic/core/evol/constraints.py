
from enum import Enum
import re

class Cstr_type(Enum):
	ONROAD = 0
	ONREGIONTYPE = 1

	NOCOLLISION = 10
	NOTONSAMEROAD = 11

	CANSEE = 20

	HASTOLEFT = 30
	HASTORIGHT = 31
	HASBEHIND = 32
	HASINFRONT = 33

	DISTCLOSE = 40
	DISTMED = 41
	DISTFAR = 42

	DOINGMANEUVER = 50

	COLLIDINGPATHS = 60
	COLLIDINGPATHSAHEAD = 61
	COLLIDINGPATHSAHEADTIMED = 62

	SP_NONE = 100
	SP_SLOW = 101
	SP_MED = 102
	SP_FAST = 103

	BE_NONE = 110
	BE_FOLLOW = 111
	BE_MERGE_LEFT = 112
	BE_MERGE_RIGHT = 113
	BE_SLOWDOWN = 114
	BE_SPEEDUP = 115
	BE_FOLLOW_AVOID = 116
	BE_SCENIC = 117
	
	OLDCOLLIDESATMANEUVER = 200


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
	
class Cstr_util:

	PRIORITY = {Cstr_type.DOINGMANEUVER: 0,
	     Cstr_type.DISTCLOSE:1,
		 Cstr_type.DISTMED:1,
		 Cstr_type.DISTFAR:1}

	def parseConfigConstraints(params, keyword):
		# Parse constraints from config file
		str_cons = params.get(keyword)
		if str_cons == None:
			return []
		list_cons = str_cons.split(';')
		parsed_cons = []

		# since last constraint also has a ";" at the end, we ignore last split
		for con_str in list_cons[:-1]:
			if con_str.strip().startswith('#'):
				# commented constraints
				continue

			res = re.search(r"\s*(\w*) : \[(\d*), (-?\d*|[a-z_]*)\]", con_str)
			con_type = Cstr_type[res.group(1)]
			id1 = int(res.group(2))
			try:
				id2 = int(res.group(3))
			except ValueError:
				id2 = res.group(3)
			con = Cstr(con_type, id1, id2)
			parsed_cons.append(con)
		
		# Reorder according to priority
		parsed_cons = sorted(parsed_cons, key=lambda c: c.type in Cstr_util.PRIORITY, reverse=True)

		return parsed_cons
