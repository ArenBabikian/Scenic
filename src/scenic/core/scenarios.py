"""Scenario and scene objects."""

from copy import Error, copy
from enum import Enum
import os
import random
import re
import copy
import time
from numpy.core.numeric import full
from pymoo.util.termination.collection import TerminationCollection

from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from pymoo.util.termination.max_time import TimeBasedTermination
from scenic.core.nsga2mod import NSGA2M
from scenic.core.OneSolutionHeuristicTermination import OneSolutionHeuristicTermination

from scenic.core.distributions import Samplable, RejectionException, needsSampling
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.external_params import ExternalSampler
from scenic.core.regions import EmptyRegion
from scenic.core.workspaces import Workspace
from scenic.core.vectors import Vector
from scenic.core.utils import areEquivalent, DefaultIdentityDict
from scenic.core.errors import InvalidScenarioError
from scenic.core.dynamics import Behavior
from scenic.core.requirements import BoundRequirement
from scenic.domains.driving.roads import Network
from scenic.simulators.utils.colors import Color

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

class Scene:
	"""Scene()

	A scene generated from a Scenic scenario.

	Attributes:
		objects (tuple of :obj:`~scenic.core.object_types.Object`): All objects in the
		  scene. The ``ego`` object is first.
		egoObject (:obj:`~scenic.core.object_types.Object`): The ``ego`` object.
		params (dict): Dictionary mapping the name of each global parameter to its value.
		workspace (:obj:`~scenic.core.workspaces.Workspace`): Workspace for the scenario.
	"""
	def __init__(self, workspace, objects, egoObject, params,
				 alwaysReqs=(), terminationConds=(), termSimulationConds=(),
				 recordedExprs=(), recordedInitialExprs=(), recordedFinalExprs=(),
				 monitors=(), behaviorNamespaces={}, dynamicScenario=None):
		self.workspace = workspace
		self.objects = tuple(objects)
		self.egoObject = egoObject
		self.params = params
		self.alwaysRequirements = tuple(alwaysReqs)
		self.terminationConditions = tuple(terminationConds)
		self.terminateSimulationConditions = tuple(termSimulationConds)
		self.recordedExprs = tuple(recordedExprs)
		self.recordedInitialExprs = tuple(recordedInitialExprs)
		self.recordedFinalExprs = tuple(recordedFinalExprs)
		self.monitors = tuple(monitors)
		self.behaviorNamespaces = behaviorNamespaces
		self.dynamicScenario = dynamicScenario

	def show(self, zoom=None, dirPath=None, saveImages=False, viewImages=False, block=True):
		"""Render a schematic of the scene for debugging."""
		import matplotlib.pyplot as plt
		fig = plt.figure()
		plt.gca().set_aspect('equal')
		# display map
		self.workspace.show(plt)
		# draw objects
		for obj in self.objects:
			obj.show(self.workspace, plt, highlight=(obj is self.egoObject))
		# zoom in if requested
		if zoom != None:
			self.workspace.zoomAround(plt, self.objects, expansion=zoom)
		
		if saveImages:
			filePath = f'{dirPath}/image.png'
			fig.savefig(filePath)
			print(f'  Saved image at                {filePath}')
		if viewImages:
			plt.show(block=block)

	def saveExactCoords(self, path=None):
		filePath = f'{path}/exact.scenic'
		ego = self.egoObject
		with open(filePath, "w") as f:
			mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
			f.write(f'param map = localPath(\'{mapPath}\')\n')
			f.write('model scenic.simulators.carla.model\n')
			f.write('\n')
			# Actor initializations
			for i in range(len(self.objects)):
				o = self.objects[i]
				oName = f'o{i}'
				if o is ego:
					oName = 'ego'
				col = o.color
				if type(col) is Color:
					col = [col.r, col.g, col.b]
				f.write(f'{oName} = Car at {o.position}, with color{o.color}\n')
		print(f'  Saved exact coordinates at    {filePath}')

	def getAbsScene(self, path=None):
		stats = {}
		all_heur = {}
		accepted_cstrs = []
		# NOTE: ignoring bidirectional relations
		for i in range(len(self.objects)):
			oi = self.objects[i]
			# for j in range(i+1, len(self.objects)):
			for j in range(len(self.objects)):
				if i == j:
					continue

				# BIDIRECTIONAL
				
				oj = self.objects[j]
				cur_heur = {}

				# POSITION CSTRS
				if oi.toLeftHeuristic(oj) == 0:
					con_type = Cstr_type['HASTOLEFT']
					accepted_cstrs.append(Cstr(con_type, i, j))
				if oi.toRightHeuristic(oj) == 0:
					con_type = Cstr_type['HASTORIGHT']
					accepted_cstrs.append(Cstr(con_type, i, j))
				if oi.inFrontHeuristic(oj) == 0:
					con_type = Cstr_type['HASINFRONT']
					accepted_cstrs.append(Cstr(con_type, i, j))
				if oi.behindHeuristic(oj) == 0:
					con_type = Cstr_type['HASBEHIND']
					accepted_cstrs.append(Cstr(con_type, i, j))

				# CANSEE CSTRS
				val_canSee = oi.canSeeHeuristic(oj)
				cur_heur['CANSEE-A'] = val_canSee
				if val_canSee == 0:
					accepted_cstrs.append(Cstr(Cstr_type['CANSEE'], i, j))

				# UNIDIRECTIONAL
				# only consider distance once, because it is symetric
				if i < j:
					continue

				# DISTANCE CSTRS
				val_close = oi.distCloseHeuristic(oj)
				val_med = oi.distMedHeuristic(oj)
				val_far = oi.distFarHeuristic(oj)
				cur_heur['DISTCLOSE'] = val_close
				cur_heur['DISTMED'] = val_med
				cur_heur['DISTFAR'] = val_far

				# Below is mathematical obligation
				vals_dist = [val_close, val_med, val_far]
				kw = ['DISTCLOSE', 'DISTMED', 'DISTFAR']
				con_type = Cstr_type[kw[vals_dist.index(0)]]
				accepted_cstrs.append(Cstr(con_type, i, j))

				# Add to all heuristics
				ind = (i, j)
				all_heur[ind] = cur_heur

		# sort constraints wrt. type
		accepted_cstrs.sort(key=lambda x: x.type.value)
		n_obj = len(self.objects)
		n_hard_cons = n_obj + (n_obj * (n_obj-1))/2 #onroad + nocollisions
		stats['num_cons'] = n_hard_cons + len(accepted_cstrs)
		stats['num_hard_cons'] = n_hard_cons
		stats['num_soft_cons'] = len(accepted_cstrs)
		stats['all'] = [str(c) for c in accepted_cstrs]

		# NSGA : includes all constraints (full repr of abs scen)
		self.generateNsgaConfig(accepted_cstrs, path)

		# Scenic : some things are not representible
		sorted_cstrs = self.seperateByType(accepted_cstrs)
		del_sc1 = self.generateVeneerRequireConfig(copy.deepcopy(sorted_cstrs), path)
		stats['deleted-sc1'] = del_sc1
		del_sc2 = self.generateRegionRequireConfig(copy.deepcopy(sorted_cstrs), path)
		stats['deleted-sc2'] = del_sc2
		del_sc3 = self.generateRegionOnlyConfig(copy.deepcopy(accepted_cstrs), path)
		stats['deleted-sc3'] = del_sc3

		return stats

		

	def generateNsgaConfig(self, constraints, path):
		filePath = f'{path}/d-nsga.scenic'
		with open(filePath, "w") as f:

			mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
			f.write(f'param map = localPath(\'{mapPath}\')\n')
			f.write('param constraints = \" \\')

			# Default constraints
			for i in range(len(self.objects)):
				f.write(f'ONROAD : [{i}, -1]; \\\n')
			for i in range(len(self.objects)):
				for j in range(i+1, len(self.objects)):
					f.write(f'NOCOLLISION : [{i}, {j}]; \\\n')

			# Added constraints
			for c in constraints:
				f.write(f'{c} \\\n')
			f.write('\"\n')
			f.write('model scenic.simulators.carla.model\n')
			f.write('\n')

			# Actor initializations
			ind_to_name = self.get_actor_names()
			for i in range(len(self.objects)):
				col = self.objects[i].color
				if type(col) is Color:
					col = [col.r, col.g, col.b]
				f.write(f'{ind_to_name[i]} = Car with color{col}\n')

		print(f'  Saved nsga config file at     {filePath}')


	def seperateByType(self, constraints):
		canSeeCstrs = []
		posCstrs = []
		distCstrs = []

		# seperate constraints
		for c in constraints:
			if c.type.value == 3:
				canSeeCstrs.append(c)
			elif c.type.value >= 4 and c.type.value <= 7:
				posCstrs.append(c)
			elif c.type.value >= 8 and c.type.value <= 10:
				distCstrs.append(c)
			else:
				raise Error('incorrect constraint type')

		return [canSeeCstrs, posCstrs, distCstrs]


	def most_common_cstr(self, cycles):
		# get a full list of involved constraints, with repetition
		full_list = []
		for x in cycles:
			full_list.extend(x)

		# find most common constraint in the cycles
		return max(set(full_list), key=full_list.count)


	def most_common_pair(self, cycles):
		# get a full list of involved constraints, with repetition
		all_pairs = []
		for cyc in cycles:
			for con in cyc:
				all_pairs.append((con.src, con.tgt))

		# find most common constraint in the cycles
		return max(set(all_pairs), key=all_pairs.count)


	def find_ordering(self, constraints):
		copyCstrs = constraints.copy()
		toBePlaced = list(range(len(self.objects)))
		ordering = []

		while len(ordering) < len(self.objects):
			for i in toBePlaced:

				#check if depends on anything
				if not list(filter(lambda x : x.tgt == i, copyCstrs)):
					# i depends on nothing (above is empty)
					ordering.append(i)
					toBePlaced.remove(i)
					copyCstrs = list(filter(lambda x : x.src != i, copyCstrs))
					break
		
		return ordering


	def findCycles(self, deps):

		# TODO improve this! This is embarassing :(

		# BUG : [0, 2] - [2, 0] - [0, 2] - [2, 0]
		max = len(self.objects)
		cycles = []

		if max < 1: return cycles

		for c in list(filter(lambda x : x.src == x.tgt, deps)):
			cycles.append([c]) 

		if max < 2: return cycles
		
		for c1 in deps:
			for c2 in list(filter(lambda x : x.src == c1.tgt and x.tgt == c1.src, deps)):
				cycles.append([c1, c2]) 

		if max < 3: return cycles

		for c1 in deps:
			for c2 in list(filter(lambda x : x.src == c1.tgt, deps)):
				for c3 in list(filter(lambda y : y.src == c2.tgt and y.tgt == c1.src, deps)):
					cycles.append([c1, c2, c3])

		if max < 4: return cycles

		for c1 in deps:
			for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
				for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
					for c4 in list(filter(lambda y : y.src == c3.tgt and y.tgt == c1.src, deps)):
						cycles.append([c1, c2, c3, c4])

		if max < 5: return cycles

		for c1 in deps:
			for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
				for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
					for c4 in list(filter(lambda x : x.src == c3.tgt, deps)):
						for c5 in list(filter(lambda y : y.src == c4.tgt and y.tgt == c1.src, deps)):
							cycles.append([c1, c2, c3, c4, c5])

		if max < 6: return cycles


	def get_actor_names(self):
		ego = self.egoObject
		ind_to_name = {}
		for i in range(len(self.objects)):
			o = self.objects[i]
			oName = f'o{i}'
			if o is ego:
				oName = 'ego'
			ind_to_name[i] = oName

		return ind_to_name


	def generateVeneerRequireConfig(self, sorted_constraints, path):
		
		# PosRel : Veneer
		# DistRel : Veneer if hasAssociatedPosRel else require
		# canSee : require

		# Represenatability
		# posRel cycles = NO
		# canSee cycles = YES
		# obj w/ multi dependencies = NO

		### PREP

		# Initialize relevant sets
		removedCstrs = []
		canSeeCstrs, posCstrs, distCstrs = sorted_constraints

		# 1. handle cycles
		cycles = self.findCycles(posCstrs)
		# for x in cycles:
		# 	print(x)

		while cycles:
			# find most common constraint
			most_common = self.most_common_cstr(cycles)
			# print(f'REMOVED: <{most_common}>')

			#remove the most common constraint
			posCstrs.remove(most_common)
			removedCstrs.append(most_common)

			#check if cycles are left
			cycles = self.findCycles(posCstrs)

			# for x in cycles:
			# 	print(x)

		# 2. find ordering
		# print('------REMAINING------')
		# for c in posCstrs:
		# 	print(c)

		ordering = self.find_ordering(posCstrs)
		# print(f'ordering = {ordering}')
		

		# 3. handle objects w/ multiple dependencies
		# print('------MULTI-DEP------')
		for i in range(len(self.objects)):
			deps = list(filter(lambda x : x.tgt == i, posCstrs))
			# print(f'{i} = {deps}')
			if len(deps) > 1:
				numToDel = len(deps) - 1
				for _ in range(numToDel):
					itemToDel = random.choice(deps)
					posCstrs.remove(itemToDel)
					deps.remove(itemToDel)
					removedCstrs.append(itemToDel)


		# print(f'REMOVED ALL = {removedCstrs}')
		
		### START WRITING FILE
		# At this stage, we have: canSee, posRel, distRel, removed Constraints

		ind_to_name = self.get_actor_names()
		filePath = f'{path}/d-sc1.scenic'
		with open(filePath, "w") as f:
			mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
			f.write(f'param map = localPath(\'{mapPath}\')\n')

			### handle REMOVED constraints
			if removedCstrs:
				f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
				f.write('# Thus we removed these constraints to make it representible\n')
				f.write('param constraints = \" \\\n')
				for c in removedCstrs:
					f.write(f'{c} \\\n')
				f.write('\"\n')

			f.write('model scenic.simulators.carla.model\n')
			f.write('\n')

			### handle POSITION constraints + possibly DISTANCE

			# initialise the actor
			for i in ordering:
				posDepsOfi = list(filter(lambda x : x.tgt == i, posCstrs))
				if len(posDepsOfi) > 1:
					raise Error('Some kind of cycle error!')

				postext = ""
				# Handle positions
				if len(posDepsOfi) == 1:
					posDep = posDepsOfi[0]
					if posDep.type.value == 4:
						direction = "left of"
					if posDep.type.value == 5:
						direction = "right of"
					if posDep.type.value == 6:
						direction = "behind"
					if posDep.type.value == 7:
						direction = "ahead of"
					posCstrs.remove(posDep)

					s = posDep.src
					t = i

					# Handle distances (if any)
					distDeps = list(filter(lambda x : (x.src == s and x.tgt == t) or (x.src == t and x.tgt == s), distCstrs))
					if len(distDeps) > 1:
						raise Error('multiple distance constraints!!!')

					lb, ub = 0, 50
					if len(distDeps) == 1:
						distDep = distDeps[0]					
						if distDep.type.value == 8:
							lb, ub = 0, 10
						if distDep.type.value == 9:
							lb, ub = 10, 20
						if distDep.type.value == 10:
							lb, ub = 20, 50
						distCstrs.remove(distDep)

					postext = f'{direction} {ind_to_name[s]} by Range({lb}, {ub}), '

				# assign color
				col = self.objects[i].color
				if type(col) is Color:
					col = [col.r, col.g, col.b]
				f.write(f'{ind_to_name[i]} = Car {postext}with color{col}\n')

			if posCstrs:
				raise Error('Remaining position constraints!!')

			f.write('\n')

			### handle VISIBILITY constraints
			for c in canSeeCstrs:
				f.write(f'require {ind_to_name[c.src]} can see {ind_to_name[c.tgt]}\n')

			### handle remaining DISTANCE constraints
			for c in distCstrs:
				src = ind_to_name[c.src]
				tgt = ind_to_name[c.tgt]					
				if c.type.value == 8:
					f.write(f'require (distance from {src} to {tgt}) <= 10 \n')
				if c.type.value == 9:
					f.write(f'require 10 <= (distance from {src} to {tgt}) <= 20 \n')
				if c.type.value == 10:
					f.write(f'require 20 <= (distance from {src} to {tgt}) <= 50 \n')

		print(f'  Saved ven-req config file at  {filePath}')
		return [str(c) for c in removedCstrs]

	def generateRegionOnlyConfig(self, allConstraints, path):
		
		# PosRel : Region
		# DistRel : Region
		# canSee : Region

		# Represenatability
		# posRel cycles = NO
		# canSee cycles = NO
		# obj w/ multi dependencies = YES

		### PREP

		# Initialize relevant sets
		removedCstrs = []
		
		# 1. handle cycles
		
		cycles = self.findCycles(allConstraints)

		while cycles:
			# find most common constraint
			most_common_src, most_common_tgt = self.most_common_pair(cycles)

			#remove the most common constraint
			toRemove = list(filter(lambda x : x.src == most_common_src and x.tgt == most_common_tgt, allConstraints))
			for c in toRemove:
				allConstraints.remove(c)
				removedCstrs.append(c)

			#check if cycles are left
			cycles = self.findCycles(allConstraints)

		# 2. find ordering
		ordering = self.find_ordering(allConstraints)
		
		### START WRITING FILE
		# At this stage, we have: canSee, posRel, distRel, removed Constraints
		ind_to_name = self.get_actor_names()
		filePath = f'{path}/d-sc3.scenic'
		with open(filePath, "w") as f:
			mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
			f.write(f'param map = localPath(\'{mapPath}\')\n')

			### handle REMOVED constraints
			if removedCstrs:
				f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
				f.write('# Thus we removed these constraints to make it representible\n')
				f.write('param constraints = \" \\\n')
				for c in removedCstrs:
					f.write(f'{c} \\\n')
				f.write('\"\n')

			f.write('model scenic.simulators.carla.model\n')
			f.write('\n')

			### handle ALL constraints (as regions)

			# initialise the actors
			for i in ordering:
				posDepsOfi = list(filter(lambda x : x.tgt == i, allConstraints))
				reg = ""
				# Handle positions
				for d in posDepsOfi:
					addIntersect = reg
					if addIntersect:
						reg += ".intersect("

					s_name = ind_to_name[d.src]
					if d.type.value == 3:
						# CANSEE
						reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.radians(22.5))'
					if d.type.value == 4:
						# HASTOLEFT
						reg += f'SectorRegion({s_name}, 20, {s_name}.heading+(math.pi/2), math.atan(2.5/2))'
					if d.type.value == 5:
						# HASTORIGHT
						reg += f'SectorRegion({s_name}, 20, {s_name}.heading-(math.pi/2), math.atan(2.5/2))'
					if d.type.value == 6:
						# HASBEHIND
						reg += f'SectorRegion({s_name}, 50, {s_name}.heading+math.pi, math.atan(2/5))'
					if d.type.value == 7:
						# HASINFRONT
						reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.atan(2/5))'
					if d.type.value == 8:
						# DISTCLOSE
						reg += f'CircularRegion({s_name}, 10)'
					if d.type.value == 9:
						# DISTMED
						reg += f'CircularRegion({s_name}, 20)'
						if addIntersect : reg += ")"
						reg += f'.difference(CircularRegion({s_name}, 10)'
						if not addIntersect : reg += ")"
					if d.type.value == 10:
						# DISTFAR
						reg += f'CircularRegion({s_name}, 50)'
						if addIntersect : reg += ")"
						reg += f'.difference(CircularRegion({s_name}, 20)'
						if not addIntersect : reg += ")"
					allConstraints.remove(d)
					
					if addIntersect:
						reg += ")"
			
				if reg:
					reg = f'in {reg}, '

				# assign color
				col = self.objects[i].color
				if type(col) is Color:
					col = [col.r, col.g, col.b]
				f.write(f'{ind_to_name[i]} = Car {reg}with color{col}\n')

			if allConstraints:
				raise Error('Remaining constraints!!')

		print(f'  Saved reg-onl config file at  {filePath}')
		return [str(c) for c in removedCstrs]

	def generateRegionRequireConfig(self, sorted_constraints, path):
		
		# PosRel : Region
		# DistRel : require
		# canSee : require

		# Represenatability
		# posRel cycles = NO
		# canSee cycles = YES
		# obj w/ multi dependencies = YES

		### PREP

		# Initialize relevant sets
		removedCstrs = []
		canSeeCstrs, posCstrs, distCstrs = sorted_constraints

		# 1. handle cycles
		cycles = self.findCycles(posCstrs)

		while cycles:
			# find most common constraint
			most_common = self.most_common_cstr(cycles)

			#remove the most common constraint
			posCstrs.remove(most_common)
			removedCstrs.append(most_common)

			#check if cycles are left
			cycles = self.findCycles(posCstrs)

		# 2. find ordering
		ordering = self.find_ordering(posCstrs)
		
		### START WRITING FILE
		# At this stage, we have: canSee, posRel, distRel, removed Constraints
		ind_to_name = self.get_actor_names()
		filePath = f'{path}/d-sc2.scenic'
		with open(filePath, "w") as f:
			mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
			f.write(f'param map = localPath(\'{mapPath}\')\n')

			### handle REMOVED constraints
			if removedCstrs:
				f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
				f.write('# Thus we removed these constraints to make it representible\n')
				f.write('param constraints = \" \\\n')
				for c in removedCstrs:
					f.write(f'{c} \\\n')
				f.write('\"\n')

			f.write('model scenic.simulators.carla.model\n')
			f.write('\n')

			### handle POSITION constraints (as regions)

			# initialise the actors
			for i in ordering:
				posDepsOfi = list(filter(lambda x : x.tgt == i, posCstrs))
				reg = ""

				# Handle positions
				for d in posDepsOfi:
					addIntersect = reg
					if addIntersect:
						reg += ".intersect("

					s_name = ind_to_name[d.src]
					if d.type.value == 4:
						# HASTOLEFT
						reg += f'SectorRegion({s_name}, 20, {s_name}.heading+(math.pi/2), math.atan(2.5/2))'
					if d.type.value == 5:
						# HASTORIGHT
						reg += f'SectorRegion({s_name}, 20, {s_name}.heading-(math.pi/2), math.atan(2.5/2))'
					if d.type.value == 6:
						# HASBEHIND
						reg += f'SectorRegion({s_name}, 50, {s_name}.heading+math.pi, math.atan(2/5))'
					if d.type.value == 7:
						# HASINFRONT
						reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.atan(2/5))'
					posCstrs.remove(d)
					
					if addIntersect:
						reg += ")"
			
				if reg:
					reg = f'in {reg}, '

				# assign color
				col = self.objects[i].color
				if type(col) is Color:
					col = [col.r, col.g, col.b]
				f.write(f'{ind_to_name[i]} = Car {reg}with color{col}\n')

			if posCstrs:
				raise Error('Remaining position constraints!!')

			f.write('\n')

			### handle VISIBILITY constraints
			for c in canSeeCstrs:
				f.write(f'require {ind_to_name[c.src]} can see {ind_to_name[c.tgt]}\n')

			### handle remaining DISTANCE constraints
			for c in distCstrs:
				src = ind_to_name[c.src]
				tgt = ind_to_name[c.tgt]					
				if c.type.value == 8:
					f.write(f'require (distance from {src} to {tgt}) <= 10 \n')
				if c.type.value == 9:
					f.write(f'require 10 <= (distance from {src} to {tgt}) <= 20 \n')
				if c.type.value == 10:
					f.write(f'require 20 <= (distance from {src} to {tgt}) <= 50 \n')

		print(f'  Saved reg-req config file at  {filePath}')
		return [str(c) for c in removedCstrs]


class Scenario:
	"""Scenario()

	A compiled Scenic scenario, from which scenes can be sampled.
	"""
	def __init__(self, workspace, simulator,
				 objects, egoObject,
				 params, externalParams,
				 requirements, requirementDeps,
				 monitors, behaviorNamespaces,
				 dynamicScenario):
		if workspace is None:
			workspace = Workspace()		# default empty workspace
		self.workspace = workspace
		self.simulator = simulator		# simulator for dynamic scenarios
		# make ego the first object, while otherwise preserving order
		ordered = []
		for obj in objects:
			if obj is not egoObject:
				ordered.append(obj)
		self.objects = (egoObject,) + tuple(ordered) if egoObject else tuple(ordered)
		self.egoObject = egoObject
		self.params = dict(params)
		self.nsga = params.get('nsga') == "True"
		self.noValidation = self.nsga or params.get('no-validation') == "True"
		self.timeout = None if not params.get('timeout') else int(self.params.get('timeout'))
		self.externalParams = tuple(externalParams)
		self.externalSampler = ExternalSampler.forParameters(self.externalParams, self.params)
		self.monitors = tuple(monitors)
		self.behaviorNamespaces = behaviorNamespaces
		self.dynamicScenario = dynamicScenario
		self.network = Network.fromFile(self.params['map'])

		staticReqs, alwaysReqs, terminationConds = [], [], []
		self.requirements = tuple(dynamicScenario._requirements)	# TODO clean up
		self.alwaysRequirements = tuple(dynamicScenario._alwaysRequirements)
		self.terminationConditions = tuple(dynamicScenario._terminationConditions)
		self.terminateSimulationConditions = tuple(dynamicScenario._terminateSimulationConditions)
		self.initialRequirements = self.requirements + self.alwaysRequirements
		assert all(req.constrainsSampling for req in self.initialRequirements)
		self.recordedExprs = tuple(dynamicScenario._recordedExprs)
		self.recordedInitialExprs = tuple(dynamicScenario._recordedInitialExprs)
		self.recordedFinalExprs = tuple(dynamicScenario._recordedFinalExprs)
		# dependencies must use fixed order for reproducibility
		paramDeps = tuple(p for p in self.params.values() if isinstance(p, Samplable))
		behaviorDeps = []
		for namespace in self.behaviorNamespaces.values():
			for value in namespace.values():
				if isinstance(value, Samplable):
					behaviorDeps.append(value)
		self.dependencies = self.objects + paramDeps + tuple(requirementDeps) + tuple(behaviorDeps)

		if not self.noValidation:
			self.validate()

	def isEquivalentTo(self, other):
		if type(other) is not Scenario:
			return False
		return (areEquivalent(other.workspace, self.workspace)
			and areEquivalent(other.objects, self.objects)
			and areEquivalent(other.params, self.params)
			and areEquivalent(other.externalParams, self.externalParams)
			and areEquivalent(other.requirements, self.requirements)
			and other.externalSampler == self.externalSampler)

	def containerOfObject(self, obj):
		if hasattr(obj, 'regionContainedIn') and obj.regionContainedIn is not None:
			return obj.regionContainedIn
		else:
			return self.workspace.region

	def validate(self):
		"""Make some simple static checks for inconsistent built-in requirements.

		:meta private:
		"""
		objects = self.objects
		staticVisibility = self.egoObject and not needsSampling(self.egoObject.visibleRegion)
		staticBounds = [self.hasStaticBounds(obj) for obj in objects]
		for i in range(len(objects)):
			oi = objects[i]
			container = self.containerOfObject(oi)
			# Trivial case where container is empty
			if isinstance(container, EmptyRegion):
				raise InvalidScenarioError(f'Container region of {oi} is empty')
			# skip objects with unknown positions or bounding boxes
			if not staticBounds[i]:
				continue
			# Require object to be contained in the workspace/valid region
			if not needsSampling(container) and not container.containsObject(oi):
				raise InvalidScenarioError(f'Object at {oi.position} does not fit in container')
			# Require object to be visible from the ego object
			if staticVisibility and oi.requireVisible is True and oi is not self.egoObject:
				if not self.egoObject.canSee(oi):
					raise InvalidScenarioError(f'Object at {oi.position} is not visible from ego')
			if not oi.allowCollisions:
				# Require object to not intersect another object
				for j in range(i):
					oj = objects[j]
					if oj.allowCollisions or not staticBounds[j]:
						continue
					if oi.intersects(oj):
						raise InvalidScenarioError(f'Object at {oi.position} intersects'
												   f' object at {oj.position}')

	def fillSample(self, coords):
		for i in range(len(self.objects)):
			vi = self.objects[i]

			# Notes: coords = [x_a0, y_a0, x_a1, y_a1, ...]
			val_x = coords[2*i]
			val_y = coords[2*i + 1]
			v = Vector(val_x, val_y)

			vi.position = v
			vi.heading = self.network._defaultRoadDirection(v)
	
	def heuristic(self, x, constraints, fun):

		# return a 3-item list [distance from visibility, travel distance to avoid intersection, distance from contained region]
		objects = self.objects
		# x = [  97.64237302, -236.70268295,  -14.74759737,  -98.51499928,   -5.88366596, -109.51614019,   -7.30336197,  -99.24476481]
		self.fillSample(x)

		totCont, totVis, totColl = 0, 0, 0
		totPosRel, totDistRel = 0, 0

		## GET HEURISTIC VALUES
		## Assuming that ego position in actor llist does not change
		for c in constraints:
			vi = objects[c.src]
			vj = None
			if c.tgt != -1:
				vj = objects[c.tgt]
			
			# Constraints Switch
			if c.type == Cstr_type.ONROAD:
				### How far is the farthest corner of vi from a valid region that can contain it?
				container = self.containerOfObject(vi)
				totCont += vi.containedHeuristic(container)
			if c.type == Cstr_type.NOCOLLISION:
				### Are vi and vj intersecting?
				if vi.intersects(vj):
					totColl += 10
			if c.type == Cstr_type.CANSEE:
				### How far is vj from being visible wrt. to vi?
				totVis += vi.canSeeHeuristic(vj)

			if c.type == Cstr_type.HASTOLEFT:
				totPosRel += vi.toLeftHeuristic(vj)
			if c.type == Cstr_type.HASTORIGHT:
				totPosRel += vi.toRightHeuristic(vj)
			if c.type == Cstr_type.HASBEHIND:
				totPosRel += vi.behindHeuristic(vj)
			if c.type == Cstr_type.HASINFRONT:
				totPosRel += vi.inFrontHeuristic(vj)

			if c.type == Cstr_type.DISTCLOSE:
				totDistRel += vi.distCloseHeuristic(vj)
			if c.type == Cstr_type.DISTMED:
				totDistRel += vi.distMedHeuristic(vj)
			if c.type == Cstr_type.DISTFAR:
				totDistRel += vi.distFarHeuristic(vj)

		# print([totVis, totCont, totColl, totPosRel, totDistRel])
		# exit()
		return [fun[0](totCont), fun[1](totColl), fun[2](totVis), fun[3](totPosRel), fun[4](totDistRel)]

	def hasStaticBounds(self, obj):
		if needsSampling(obj.position):
			return False
		if any(needsSampling(corner) for corner in obj.corners):
			return False
		return True

	def getNsgaNDSs(self, constraints, funcs, verbosity):
		scenario = self
		objects = self.objects
		tot_var = len(objects)*2
		map_name = os.path.basename(self.params.get('map'))
		bounds = []
		if map_name == "town02.xodr":
			bounds = [-15, -315, 200, -98]
		if map_name == "tram05.xodr":
			bounds = [-155, -101, 103, 80]
		if map_name == "zalafullcrop.xodr":
			bounds = [-59, 1337, 211, 1811] # full smart-city section
			# bounds = [-59, 211, 1337, 1811] # smaller version

		loBd, hiBd = [], []
		for _ in range(len(objects)):
			# TODO currently hard-coded wrt. the map
			loBd.extend(bounds[:2])
			hiBd.extend(bounds[2:])
		
		class MyProblem(ElementwiseProblem):
			def __init__(self):
				super().__init__(n_var=tot_var, n_obj=5, n_constr=0,
								xl=loBd, xu=hiBd)

			# Notes: x = [x_a0, y_a0, x_a1, y_a1, ...]
			def _evaluate(self, x, out, *args, **kwargs):
				heuristics = scenario.heuristic(x, constraints, funcs)
				# out["G"] = heuristics[:2]
				# out["F"] = heuristics[2:]
				out["F"] = heuristics
		
		
		if verbosity >= 2:
			print("--Running NSGA--")   
		problem = MyProblem()
		# algorithm = GA(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
		algorithm = NSGA2M(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
		# algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)

		# n_par = self.params.get('nsga-Iters')
		# n = n_par if n_par is not None else 100
		# termination = get_termination("n_gen", n)
		# termination = MultiObjectiveSpaceToleranceTermination(tol=0.0025,
		# 														n_last=10,
		# 														n_max_gen=n)
		# TEMP
		# t1 = MultiObjectiveSpaceToleranceTermination(tol=0.0025, n_last=30)	
		# t1 = ConstraintViolationToleranceTermination(n_last=20, tol=1e-6,)	
		# t1 = IGDTermination	
		t1 = OneSolutionHeuristicTermination(heu_vals=[0, 0, 0, 0, 0])
		t2 = TimeBasedTermination(max_time=self.timeout)
		termination = TerminationCollection(t1, t2)

		# FOR REPEATABILITY: use seed=1 option
		res = minimize(problem, algorithm, termination, save_history=True, verbose=(verbosity > 1))
		return res
	
	def parseConfigConstraints(self):
		# Parse constraints from config file
		str_cons = self.params.get('constraints')
		if str_cons == None:
			return []
		list_cons = str_cons.split(';')
		parsed_cons = []

		# since last constraint also has a ";" at the end, we ignore last split
		for con_str in list_cons[:-1]:
			res = re.search(r"\s*(\w*) : \[(\d*), (-?\d*)\]", con_str)
			con_type = Cstr_type[res.group(1)]
			id1 = int(res.group(2))
			id2 = int(res.group(3))
			con = Cstr(con_type, id1, id2)
			parsed_cons.append(con)
		
		return parsed_cons

	def generate(self, maxIterations=2000, verbosity=0, feedback=None):
		"""Sample a `Scene` from this scenario.

		Args:
			maxIterations (int): Maximum number of rejection sampling iterations.
			verbosity (int): Verbosity level.
			feedback (float): Feedback to pass to external samplers doing active sampling.
				See :mod:`scenic.core.external_params`.

		Returns:
			A pair with the sampled `Scene` and the number of iterations used.

		Raises:
			`RejectionException`: if no valid sample is found in **maxIterations** iterations.
		"""
		objects = self.objects
		allSamples = []
		historicSolSets = []

		# choose which custom requirements will be enforced for this sample
		activeReqs = [req for req in self.initialRequirements if random.random() <= req.prob]

		totalTime = -1
		iterations = 0
		failed = False
		if self.nsga:
			# If using NSGA, replace object positions in the sample
			# Custom constraints coming from parameters

			#We assume that ego is obect[0]
			parsed_cons = self.parseConfigConstraints()
			
			# [totCont, totColl, totVis, totPosRel, totDistRel]
			functions = [(lambda x:x**3),
						(lambda x:x**3),
						(lambda x:x**2),
						(lambda x:x**2),
						(lambda x:x**2)]
			nsgaRes = self.getNsgaNDSs(parsed_cons, functions, verbosity)
			totalTime = nsgaRes.exec_time

			# Get number of required nsga solutions
			measurement_outputs = False
			if not 'nsga-NumSols' in self.params:
				# Default
				numSols = 5
			else:
				if self.params.get('nsga-NumSols') == 'measurement':
					measurement_outputs = True
				else:
					val = int(self.params.get('nsga-NumSols'))
					if  val == -1:
						numSols = len(nsgaRes.F)
					else:
						numSols = min(len(nsgaRes.F), val)

			if verbosity >= 2:
				print("--Results--")
				print("f = [Cont, Coll, Vis, PosRel, DistRel]")

			if not measurement_outputs :
				# Rank the solutions by prioritising containment and collision objectives
				aggregateFitness = []
				for i in range(len(nsgaRes.F)):
					f = nsgaRes.F[i]
					aggregateFitness.append((f[0]+f[1], f[2]+f[3]+f[4], i))
					# ALTERNATE RANKING, just takes the total
					#aggregateFitness.append((sum(f), i))
				sortedFitness = sorted(aggregateFitness)
				
				# save the selected number of sols
				for i in range(numSols):
					aggFit = sortedFitness[i]
					j = aggFit[-1]
					self.fillSample(nsgaRes.X[j])
					found = False
					while not found:
						try:
							allSamples.append(Samplable.sampleAll(self.dependencies))
							found = True
						except:
							print('failed to sample')

					if verbosity >= 2:
						print(f'--Solution {i}--')
						print(f'x = {tuple([round(e, 1) for e in nsgaRes.X[j]])}')
						print(f'f = {tuple([round(e, 1) for e in nsgaRes.F[j]])}')

			else :
				# keep all solutions, and we will do selection of the required 2 later on
				for i in range(len(nsgaRes.F)):
					if verbosity >= 2:
							print(f'--Solution {i}--')
							print(f'x = {tuple([round(e, 1) for e in nsgaRes.X[i]])}')
							print(f'f = {tuple([round(e, 1) for e in nsgaRes.F[i]])}')
					self.fillSample(nsgaRes.X[i])
					found = False
					while not found:
						try:
							allSamples.append(Samplable.sampleAll(self.dependencies))
							found = True
						except:
							print('failed to sample - all')

				#only keep the intersting historic results
				# Must be in ascending order
				timesToKeep = [30, 60, 120, 180, 300, 600, 1200, 1800, 2400, 3000]
				# timesToKeep = [5, 10, 20, 30, 45]
				timeIndex = 0

				for i in range(len(nsgaRes.history)):
					solAtI = nsgaRes.history[i]
					r = solAtI.result()
					ex_t = solAtI.exec_time
					# print(f'{i}. exec={ex_t}, termin={nsgaRes.history[i].has_terminated}, tgt={timesToKeep[timeIndex]}, sol[0]={r.X[0][0]}')
					if ex_t != None and timeIndex < len(timesToKeep) and ex_t > timesToKeep[timeIndex]:
						# create a list of samples
						historicSolSets.append((ex_t, list(r.X)))
						timeIndex += 1

		else:
			# do rejection sampling until requirements are satisfied
			rejection = True
			startTime = time.time()
			while rejection is not None and not failed:
				if iterations > 0:	# rejected the last sample
					if verbosity >= 2:
						print(f'  Rejected sample {iterations} because of: {rejection}')
					if self.externalSampler is not None:
						feedback = self.externalSampler.rejectionFeedback
				if not self.timeout and iterations >= maxIterations:
					# raise RejectionException(f'failed to generate scenario in {iterations} iterations')
					failed = True
				execTime = time.time()-startTime
				if execTime > self.timeout:
					failed = True
				iterations += 1
				try:
					if self.externalSampler is not None:
						self.externalSampler.sample(feedback)
					sample = Samplable.sampleAll(self.dependencies)
				except RejectionException as e:
					rejection = e
					continue
				rejection = None
				if not self.noValidation:
					ego = sample[self.egoObject]
					# Normalize types of some built-in properties
					for obj in objects:
						sampledObj = sample[obj]
						assert not needsSampling(sampledObj)
						# position, heading
						assert isinstance(sampledObj.position, Vector)
						sampledObj.heading = float(sampledObj.heading)
						# behavior
						behavior = sampledObj.behavior
						if behavior is not None and not isinstance(behavior, Behavior):
							raise InvalidScenarioError(
								f'behavior {behavior} of Object {obj} is not a behavior')

					# Check built-in requirements
					for i in range(len(objects)):
						vi = sample[objects[i]]
						# Require object to be contained in the workspace/valid region
						container = self.containerOfObject(vi)
						if not container.containsObject(vi):
							rejection = 'object containment'
							break
						# Require object to be visible from the ego object
						if vi.requireVisible and vi is not ego and not ego.canSee(vi):
							rejection = 'object visibility'
							break
						# Require object to not intersect another object
						if not vi.allowCollisions:
							for j in range(i):
								vj = sample[objects[j]]
								if not vj.allowCollisions and vi.intersects(vj):
									rejection = 'object intersection'
									break
						if rejection is not None:
							break
					if rejection is not None:
						continue
					# Check user-specified requirements
					for req in activeReqs:
						if not req.satisfiedBy(sample):
							rejection = f'user-specified requirement (line {req.line})'
							break
			totalTime = time.time()-startTime
			if not failed:
				allSamples.append(sample)

		stats = {}
		stats['success'] = not failed # DONE
		stats['time'] = totalTime # DONE
		stats['num_iterations'] = iterations # TODO adapt to nsga

		if self.params.get('saveStats') == "True":

			# get list of included constraints
			# These are removed constraints for scenic
			# these are all constraints for NSGA
			parsed_cons = self.parseConfigConstraints()
			num_hard_cons = len(list(filter(lambda x : x.type == Cstr_type.ONROAD or x.type == Cstr_type.NOCOLLISION, parsed_cons)))
			
			# Analyse the allSamples (final set of samples)
			allVals, numVioMap, sortedGlobal, sortedHardPrio = self.analyseSolSet(parsed_cons, allSamples)

			# no stats if failed and not nsga
			if failed and not self.nsga:
				print('  Could not generate scene.')
				return [None], stats

			# nsga succeeds if best solution satisfies all constraints 
			if self.nsga and measurement_outputs:
				failed = sortedGlobal[0][0] > 0
			
			# Gather statistics
			stats['success'] = not failed # DONE

			if not self.nsga:
				#at this stage we should have exactly one solution
				if len(allSamples) != 1 :
					 raise Error('something went wrong')
				stats['CON_num_rm'] = len(parsed_cons)
				stats['CON_sat_num_rm'] = len(parsed_cons) - sum(numVioMap[allSamples[0]])
				stats['CON_sat_%_rm'] = -1 if len(parsed_cons) == 0 else stats['CON_sat_num_rm'] / len(parsed_cons)
				stats['CON_rm_vals'] = allVals[allSamples[0]]
			else:
				num_cons = len(parsed_cons)
				stats['CON_num'] = num_cons
				stats['CON_num_hard'] = num_hard_cons
				num_soft_cons = len(parsed_cons) - num_hard_cons
				stats['CON_num_soft'] = num_soft_cons
				
				allSolStats = {}
				if measurement_outputs:
					bestGlobal = allSamples[sortedGlobal[0][-1]]
					bestHardPrio = allSamples[sortedHardPrio[0][-1]]

					allSamples = [bestGlobal, bestHardPrio]
					names = ['sol_best_global', 'sol_best_Hard_Prio']
					
					for i in range(len(allSamples)):
						sol = allSamples[i]						
						solStats = {}
						solNumVioHard, solNumVioSoft = numVioMap[sol]
						solStats['CON_sat_num'] = num_cons - solNumVioHard - solNumVioSoft
						solStats['CON_sat_%'] = solStats['CON_sat_num'] / num_cons
						solStats['CON_sat_num_hard'] = num_hard_cons - solNumVioHard
						solStats['CON_sat_%_hard'] = solStats['CON_sat_num_hard'] / num_hard_cons
						solStats['CON_sat_num_soft'] = num_soft_cons - solNumVioSoft
						solStats['CON_sat_%_soft'] = solStats['CON_sat_num_soft'] / num_soft_cons
						solStats['CON_vals'] = allVals[sol]

						allSolStats[names[i]] = solStats					

				stats['solutions'] = allSolStats

			# Analyse HISTORIC sample sets
			if self.nsga:

				historyStats = {}
				for historicSolSet in reversed(historicSolSets):
					# get historic solutions as samples:
					historicSamples = []
					t = historicSolSet[0]
					historicSols = historicSolSet[1]
					for historicSol in historicSols:
						self.fillSample(historicSol)
						found = False
						while not found:
							try:
								historicSamples.append(Samplable.sampleAll(self.dependencies))
								found = True
							except:
								print('failed to sample - history')							

					allVals, numVioMap, sortedGlobal, sortedHardPrio = self.analyseSolSet(parsed_cons, historicSamples)
					
					allSolStats = {}
					if measurement_outputs:
						bestGlobal = historicSamples[sortedGlobal[0][-1]]
						bestHardPrio = historicSamples[sortedHardPrio[0][-1]]

						sampleSet = [bestGlobal, bestHardPrio]
						names = ['sol_best_global', 'sol_best_Hard_Prio']
						
						for i in range(len(sampleSet)):
							sol = sampleSet[i]						
							solStats = {}
							solNumVioHard, solNumVioSoft = numVioMap[sol]
							solStats['CON_sat_num'] = num_cons - solNumVioHard - solNumVioSoft
							solStats['CON_sat_%'] = solStats['CON_sat_num'] / num_cons
							solStats['CON_sat_num_hard'] = num_hard_cons - solNumVioHard
							solStats['CON_sat_%_hard'] = solStats['CON_sat_num_hard'] / num_hard_cons
							solStats['CON_sat_num_soft'] = num_soft_cons - solNumVioSoft
							solStats['CON_sat_%_soft'] = solStats['CON_sat_num_soft'] / num_soft_cons
							solStats['CON_vals'] = allVals[sol]

							allSolStats[names[i]] = solStats

						historyStats[t] = allSolStats

				stats['history'] = historyStats

				# print(stats)
			
		# obtained a set of valid samples; assemble scenes from it
		allScenes = []
		for sample in allSamples:
			ego = sample[self.egoObject]
			sampledObjects = tuple(sample[obj] for obj in objects)
			sampledParams = {}
			for param, value in self.params.items():
				sampledValue = sample[value]
				assert not needsLazyEvaluation(sampledValue)
				sampledParams[param] = sampledValue
			sampledNamespaces = {}
			for modName, namespace in self.behaviorNamespaces.items():
				sampledNamespace = { name: sample[value] for name, value in namespace.items() }
				sampledNamespaces[modName] = (namespace, sampledNamespace, namespace.copy())
			alwaysReqs = (BoundRequirement(req, sample) for req in self.alwaysRequirements)
			terminationConds = (BoundRequirement(req, sample)
								for req in self.terminationConditions)
			termSimulationConds = (BoundRequirement(req, sample)
								for req in self.terminateSimulationConditions)
			recordedExprs = (BoundRequirement(req, sample) for req in self.recordedExprs)
			recordedInitialExprs = (BoundRequirement(req, sample)
									for req in self.recordedInitialExprs)
			recordedFinalExprs = (BoundRequirement(req, sample)
								for req in self.recordedFinalExprs)
			scene = Scene(self.workspace, sampledObjects, ego, sampledParams,
						alwaysReqs, terminationConds, termSimulationConds,
						recordedExprs, recordedInitialExprs,recordedFinalExprs,
						self.monitors, sampledNamespaces, self.dynamicScenario)
			allScenes.append(scene)
		
		if not allScenes:
			return [None], stats
		return allScenes, stats

	def analyseSolSet(self, parsed_cons, allSamples):
		allVals = {}
		numVioMap = {}
		sortingGlobal = []
		sortingHardPrio = []

		for i in range(len(allSamples)):
			sample = allSamples[i]
			
			vals = {}
			# num_hard_cons = 0
			numVioHard = 0
			numVioSoft = 0
			for c in parsed_cons:
				vi = sample[self.objects[c.src]]
				vj = None
				if c.tgt != -1:
					vj = sample[self.objects[c.tgt]]
				if c.type == Cstr_type.ONROAD:
					vals[str(c)] = vi.containedHeuristic(self.containerOfObject(vi))
					if vals[str(c)] != 0 : numVioHard += 1
					# num_hard_cons += 1
				if c.type == Cstr_type.NOCOLLISION:
					vals[str(c)] = 1 if vi.intersects(vj) else 0
					if vals[str(c)] != 0 : numVioHard += 1
					# num_hard_cons += 1
				if c.type == Cstr_type.CANSEE:
					vals[str(c)] = vi.canSeeHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1

				if c.type == Cstr_type.HASTOLEFT:
					vals[str(c)] = vi.toLeftHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1
				if c.type == Cstr_type.HASTORIGHT:
					vals[str(c)] = vi.toRightHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1
				if c.type == Cstr_type.HASBEHIND:
					vals[str(c)] = vi.behindHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1
				if c.type == Cstr_type.HASINFRONT:
					vals[str(c)] = vi.inFrontHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1

				if c.type == Cstr_type.DISTCLOSE:
					vals[str(c)] = vi.distCloseHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1
				if c.type == Cstr_type.DISTMED:
					vals[str(c)] = vi.distMedHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1
				if c.type == Cstr_type.DISTFAR:
					vals[str(c)] = vi.distFarHeuristic(vj)
					if vals[str(c)] != 0 : numVioSoft += 1

			sortingGlobal.append((numVioHard+numVioSoft, i))
			sortingHardPrio.append((numVioHard, numVioSoft, i))
			allVals[sample] = vals
			numVioMap[sample] = [numVioHard, numVioSoft]

		# sort according to conditions
		sortedGlobal= sorted(sortingGlobal)
		sortedHardPrio = sorted(sortingHardPrio)

		return (allVals, numVioMap, sortedGlobal, sortedHardPrio)


	def resetExternalSampler(self):
		"""Reset the scenario's external sampler, if any.

		If the Python random seed is reset before calling this function, this
		should cause the sequence of generated scenes to be deterministic."""
		self.externalSampler = ExternalSampler.forParameters(self.externalParams, self.params)

	def getSimulator(self):
		if self.simulator is None:
			raise RuntimeError('scenario does not specify a simulator')
		import scenic.syntax.veneer as veneer
		return veneer.instantiateSimulator(self.simulator, self.params)

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
