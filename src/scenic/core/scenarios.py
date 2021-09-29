"""Scenario and scene objects."""

from enum import Enum
import random

from scenic.core.distributions import Samplable, RejectionException, needsSampling
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.external_params import ExternalSampler
from scenic.core.regions import EmptyRegion
from scenic.core.workspaces import Workspace
from scenic.core.vectors import Vector
from scenic.core.utils import areEquivalent
from scenic.core.errors import InvalidScenarioError
from scenic.core.dynamics import Behavior
from scenic.core.requirements import BoundRequirement
from scenic.domains.driving.roads import Network

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_termination
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

	def show(self, zoom=None, block=True):
		"""Render a schematic of the scene for debugging."""
		import matplotlib.pyplot as plt
		plt.gca().set_aspect('equal')
		# display map
		self.workspace.show(plt)
		# draw objects
		for obj in self.objects:
			print(obj.position)
			obj.show(self.workspace, plt, highlight=(obj is self.egoObject))
		# zoom in if requested
		if zoom != None:
			self.workspace.zoomAround(plt, self.objects, expansion=zoom)
		plt.show(block=block)

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

		if params.get('heuristic'):
			self.heuristic = self.heuristic()
		else:
			if not params.get('no-validation'):
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
			# print(type(oi))
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

	def fillSample(self, samp, objs, coords):
		for i in range(len(objs)):
			vi = samp[objs[i]]

			# Notes: coords = [x_a0, y_a0, x_a1, y_a1, ...]
			val_x = coords[2*i]
			val_y = coords[2*i + 1]
			v = Vector(val_x, val_y)

			vi.position = v
			vi.heading = self.network._defaultRoadDirection(v)
			# TODO ensure that ego is first pair of values
	
	def heuristic(self, x, sample, constraints):

		# return a 3-item list [distance from visibility, travel distance to avoid intersection, distance from contained region]
		objects = self.objects
		ego = sample[self.egoObject]
		self.fillSample(sample, objects, x)

		totCont = 0
		totVis = 0
		totColl = 0
		totPosRel = 0
		totDistRel = 0

		## GET HEURISTIC VALUES
		if False:
			## Assuming that ego position in actor llist does not change
			# Generic Constraints
			for i in range(len(objects)):
				vi = sample[objects[i]]

				### How far is the farthest corner of vi from a valid region that can contain it
				container = self.containerOfObject(vi)
				d = vi.containedHeuristic(container)
				totCont += d
				
				### How far is vi from being visible wrt. to ego
				if vi.requireVisible and vi is not ego:
					# ego.visibleDistance = 20
					val = ego.canSeeHeuristic(vi)
					totVis += val			

				### How many intersecting pairs are there?
				if not vi.allowCollisions:
					for j in range(i):
						vj = sample[objects[j]]
						if not vj.allowCollisions:
							if vi.intersects(vj):
								totColl += 10
		else:
			for c in constraints:
				vi = sample[objects[c.args[0]]]
				vj = None
				if c.args[1] is not None:
					vj = sample[objects[c.args[1]]]
				
				# Switch
				if c.type == Cstr_type.ONROAD:
					container = self.containerOfObject(vi)
					totCont += vi.containedHeuristic(container)
				if c.type == Cstr_type.NOCOLLISION:
					if vi.intersects(vj):
						totColl += 10
				if c.type == Cstr_type.CANSEE:
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
		return [totCont, totColl, totVis, totPosRel, totDistRel]

	def hasStaticBounds(self, obj):
		if needsSampling(obj.position):
			return False
		if any(needsSampling(corner) for corner in obj.corners):
			return False
		return True

	def getNsgaPositions(self, sample, constraints):
		scenario = self
		objects = self.objects
		tot_var = len(objects)*2
		loBd, hiBd = [], []
		for _ in range(len(objects)):
			# TODO currently hard-coded wrt. the map
			loBd.extend([-15, -315])
			hiBd.extend([200, -98])
		
		class MyProblem(ElementwiseProblem):
			def __init__(self):
				super().__init__(n_var=tot_var, n_obj=5, n_constr=0,
								xl=loBd, xu=hiBd)

			# Notes: x = [x_a0, y_a0, x_a1, y_a1, ...]
			def _evaluate(self, x, out, *args, **kwargs):
				out["F"] = scenario.heuristic(x, sample, constraints)
		
		print("--Running NSGA--")   
		problem = MyProblem()
		# algorithm = GA(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
		algorithm = NSGA2(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
		# algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)

		n_par = self.params.get('iterations')
		n = n_par if n_par is not None else 100
		termination = get_termination("n_gen", n)
		res = minimize(problem, algorithm, termination,
					seed=1, save_history=True, verbose=True)

		print("--Results--")
		print(res.X)
		print(res.F)

		# Replace positions and heading in the sample (to be sent out for generation)
		# For now, select the result set that has lowest sum
		best_id = -1
		lowest_sum = float('inf')
		for i in range(len(res.X)):
			tot = sum(res.F[i])
			if tot < lowest_sum:
				best_id = i
				lowest_sum = tot
		
		print("--Selected Solution--")
		print(f'x = {res.X[best_id]}')
		print(f'f = {res.F[best_id]}')

		self.fillSample(sample, objects, res.X[best_id])

		# TODO for now, we are only outputting one result set from the nsga.
		# Later on, we may want to output a set of scenes, one for each dsolution found by nsga.
	
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

		# choose which custom requirements will be enforced for this sample
		activeReqs = [req for req in self.initialRequirements if random.random() <= req.prob]

		# do rejection sampling until requirements are satisfied
		rejection = True
		iterations = 0
		while rejection is not None:
			if iterations > 0:	# rejected the last sample
				if verbosity >= 2:
					print(f'  Rejected sample {iterations} because of: {rejection}')
				if self.externalSampler is not None:
					feedback = self.externalSampler.rejectionFeedback
			if iterations >= maxIterations:
				raise RejectionException(f'failed to generate scenario in {iterations} iterations')
			iterations += 1
			try:
				if self.externalSampler is not None:
					self.externalSampler.sample(feedback)
				sample = Samplable.sampleAll(self.dependencies)
			except RejectionException as e:
				rejection = e
				continue
	
			# If using NSGA, replace object positions in the sample
			if self.params.get('nsga'):
				# TODO find a way to get qualitative abstractions from .scenic file
				# Custom constraints

				#We assume that ego is obect[0]
				constraints = [
					Cstr(Cstr_type.ONROAD, [0, None]),
					Cstr(Cstr_type.ONROAD, [1, None]),
					Cstr(Cstr_type.ONROAD, [2, None]),
					Cstr(Cstr_type.ONROAD, [3, None]),

					Cstr(Cstr_type.NOCOLLISION, [0, 1]),
					Cstr(Cstr_type.NOCOLLISION, [0, 2]),
					Cstr(Cstr_type.NOCOLLISION, [1, 2]),
					Cstr(Cstr_type.NOCOLLISION, [0, 3]),
					Cstr(Cstr_type.NOCOLLISION, [1, 3]),
					Cstr(Cstr_type.NOCOLLISION, [2, 3]),

					Cstr(Cstr_type.CANSEE, [0, 1]),
					
					Cstr(Cstr_type.HASTOLEFT, [1, 2]),
					Cstr(Cstr_type.HASINFRONT, [2, 3]),

					# Cstr(Cstr_type.DISTCLOSE, [1, 2]),
					Cstr(Cstr_type.DISTFAR, [1, 3])
					]
				self.getNsgaPositions(sample, constraints)

			rejection = None
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

			if not self.params.get('no-validation'):
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

		# obtained a valid sample; assemble a scene from it
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
		return scene, iterations

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
	def __init__(self, t, a):
		self.type = t
		self.args = a
