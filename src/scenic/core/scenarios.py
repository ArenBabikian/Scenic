"""Scenario and scene objects."""

from copy import Error, copy, deepcopy
import os
import random
import time
import scenic.core.evol.evol_utils as utils

from scenic.core.evol.constraints import Cstr, Cstr_type, Cstr_util
from scenic.core.distributions import Samplable, RejectionException, needsSampling
from scenic.core.evol.input_validation import validate_constraints
from scenic.core.map.map_visualisation_utils import zoomToIntersection
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.external_params import ExternalSampler
from scenic.core.regions import EmptyRegion, PolygonalRegion
from scenic.core.workspaces import Workspace
from scenic.core.vectors import Vector
from scenic.core.utils import areEquivalent
from scenic.core.errors import InvalidScenarioError
from scenic.core.dynamics import Behavior
from scenic.core.requirements import BoundRequirement
from scenic.domains.driving.roads import ManeuverType, Network
from scenic.simulators.utils.colors import Color

from collections.abc import Iterable

from pymoo.indicators.gd import GD
from pymoo.indicators.igd import IGD

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

	def show(self, zoom=None, dirPath=None, params=None, block=True, region_to_show=None):
		"""Render a schematic of the scene for debugging."""
		import matplotlib.pyplot as plt
		fig = plt.figure()
		plt.gca().set_aspect('equal')
		# display map
		self.workspace.show(plt)
		# draw objects
		for obj in self.objects:
			obj.show(self.workspace, plt, highlight=(obj is self.egoObject))
			# print(self.workspace.network.nominalDirectionsAt(obj.position))
			# print(obj.heading)

		if region_to_show is not None:
			region_to_show.show(plt, color='k')

		if params.get('view_path'):
			import scenic.core.map.map_backwards_utils as map_utils
			# Below is OLD. for when we were generating vehicles far from the intersection
			# import scenic.core.evol.map_utils as map_utils
			map_utils.handle_paths(self, params, plt, includeLongPathToIntersection=False)

		# zoom in if requested
		if zoom != None and zoom != 0:
			if self.params.get('intersectiontesting') != None:
				zoomToIntersection(self, plt)
			else:
				self.workspace.zoomAround(plt, self.objects, expansion=zoom)
		
		if params.get('save_im'):
			filePath = f'{dirPath}/image.png'
			fig.savefig(filePath)
			print(f'  Saved image at                {filePath}')
		if params.get('view_im'):
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
		self.evol = params.get('evol') == "True"
		self.noValidation = self.evol or params.get('no-validation') == "True"
		self.timeout = 10 if not params.get('timeout') else float(self.params.get('timeout'))
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

		self.handleIntersection(params)
		self.actorIdsWithManeuver = {}
		self.actorIdsSnappedToWayPoint = params.get('snapToWaypoint') if 'snapToWaypoint' in params else []

	def  handleIntersection(self, params):
		intersection_id = params.get('intersectiontesting')
		if intersection_id == None:
			self.testedIntersection = None
		else:
			intersectionsWithId = list(filter(lambda x: x.id == intersection_id, self.network.intersections))
			assert len(intersectionsWithId) == 1, f"Invalid intersection id <{intersection_id}>. Select among the following ids {[x.id for x in self.network.intersections]}"
			intersection =  intersectionsWithId[0]
			self.testedIntersection = intersection
			self.maneuverToLanes = {ManeuverType.RIGHT_TURN:[],
			    ManeuverType.LEFT_TURN:[], 
				ManeuverType.STRAIGHT:[]}
			for maneuver in intersection.maneuvers:
				conn_lane = maneuver.connectingLane
				self.maneuverToLanes[maneuver.type].append(conn_lane)

			self.maneuverToRegion = {}
			for man_type, all_regions in self.maneuverToLanes.items():
				if len(all_regions) == 0:
					self.maneuverToRegion[man_type] = None
				else:
					self.maneuverToRegion[man_type] = PolygonalRegion.unionAll(all_regions)

	
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


	def hasStaticBounds(self, obj):
		if needsSampling(obj.position):
			return False
		if any(needsSampling(corner) for corner in obj.corners):
			return False
		return True


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
		save_history = self.params.get('evol-history')

		# choose which custom requirements will be enforced for this sample
		activeReqs = [req for req in self.initialRequirements if random.random() <= req.prob]

		iterations = 0
		restarts = None
		failed = False
		if self.evol:
			# If using EVOL-ALGO, replace object positions in the sample
			# Custom constraints coming from parameters

			#We assume that ego is obect[0]
			parsed_cons = Cstr_util.parseConfigConstraints(self.params, 'constraints')

			#TODO Long-term, add some validation for the parsed constraints
			validate_constraints(self, parsed_cons)
			
			# RUN EVOLUTIONARY ALGO
			nsgaRes, heuristicTargets = utils.getEvolNDSs(self, parsed_cons, verbosity)
			totalTime = nsgaRes.exec_time
			iterations = nsgaRes.algorithm.n_gen

			# Get number of required nsga solutions
			measurement_outputs = False
			if not 'evol-NumSols' in self.params:
				# Default
				numSols = 5
			else:
				if self.params.get('evol-NumSols') == 'measurement':
					measurement_outputs = True
				else:
					val = int(self.params.get('evol-NumSols'))
					if  val == -1:
						numSols = len(nsgaRes.F)
					else:
						numSols = min(len(nsgaRes.F), val)

					if numSols > 1 and self.params.get('evol-algo') == 'ga':
						print("GA can output at most 1 solution.")
						exit(1)

			if verbosity >= 2:
				print("--Results--")
				# print("f = [Cont, Coll, Vis, PosRel, DistRel]")

			# ########### 
			# SOLUTION HANDLING
			# ###########
			if not measurement_outputs :
				# Rank the solutions by prioritising containment and collision objectives
				aggregateFitness = []
				for i in range(len(nsgaRes.F)):
					f = nsgaRes.F[i]
					# aggregateFitness.append((f[0]+f[1], f[2]+f[3]+f[4], i))
					############## TODO RETHINK THIS
					# ALTERNATE RANKING, just takes the total
					if isinstance(f, Iterable):
						fitness = sum(f)
					else:
						fitness = f
					aggregateFitness.append((fitness, i))
				sortedFitness = sorted(aggregateFitness)
				
				# save the selected number of sols
				for i in range(numSols):
					all_res = nsgaRes.X
					all_fit = nsgaRes.F
					if len(nsgaRes.X.shape) == 1:
						all_res = [all_res]
						all_fit = [all_fit]
					aggFit = sortedFitness[i]
					j = aggFit[-1]
						
					utils.fillSample(self, all_res[j])
					found = False
					while not found:
						try:
							allSamples.append(Samplable.sampleAll(self.dependencies))
							found = True
						except:
							print('failed to sample')

					if verbosity >= 2:
						print(f'--Solution {i}--')
						print(f'x = {tuple([round(e, 1) for e in all_res[j]])}')
						print(f'f = {tuple([round(e, 1) for e in all_fit[j]])}')

			else :
				# keep all solutions, and we will do selection of the required 2 later on
				all_res = nsgaRes.X
				all_fit = nsgaRes.F
				if len(nsgaRes.X.shape) == 1:
					all_res = [all_res]
					all_fit = [all_fit]
				for i in range(len(all_fit)):
					if verbosity >= 2:
							print(f'--Solution {i}--')
							print(f'x = {tuple([round(e, 1) for e in all_res[i]])}')
							print(f'f = {tuple([round(e, 1) for e in all_fit[i]])}')
					utils.fillSample(self, all_res[i])
					found = False
					while not found:
						try:
							allSamples.append(Samplable.sampleAll(self.dependencies))
							found = True
						except:
							print('failed to sample - all')

				##############################
				# Handle HISTORY data
				##############################
				if save_history != 'none':

					# Restart stats
					restarts = nsgaRes.history[-1].all_restarts

					#only keep the intersting historic results
					# Must be in ascending order
					timesToKeep = [i for i in range(0, 600, 30)]
					# timesToKeep = [i for i in range(0, 45, 2)]
					# timesToKeep = [30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600]
					# timesToKeep = [30, 60, 120, 180, 300, 600, 1200, 1800, 2400, 3000]
					# timesToKeep = [0.5, 1, 1.5, 2, 2.5, 3,3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5]
					timeIndex = 0

					for i in range(len(nsgaRes.history)):
						solAtI = nsgaRes.history[i]
						res_i = solAtI.result()
						ex_t_i = solAtI.exec_time
						# print(f'{i}. exec={ex_t}, termin={nsgaRes.history[i].has_terminated}, tgt={timesToKeep[timeIndex]}, sol[0]={r.X[0][0]}')
						if ex_t_i != None and timeIndex < len(timesToKeep) and ex_t_i > timesToKeep[timeIndex]:
							# create a list of samples
							historicSolSets.append((ex_t_i, res_i))
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
			# As such, we need to call parseConfigCons once again 
			parsed_cons = Cstr_util.parseConfigConstraints(self.params, 'constraints')
			num_hard_cons = len(list(filter(lambda x : x.type == Cstr_type.ONROAD or x.type == Cstr_type.NOCOLLISION, parsed_cons)))
			
			# Analyse the allSamples (final set of samples)
			allVals, numVioMap, sortedGlobal, sortedHardPrio = self.analyseSolSet(parsed_cons, allSamples)

			# no stats if failed and not nsga
			if failed and not self.evol:
				print('  Could not generate scene.')
				return [None], stats

			# nsga succeeds if best solution satisfies all constraints 
			if self.evol and measurement_outputs:
				failed = sortedGlobal[0][0] > 0
			
			# Gather statistics
			stats['success'] = not failed # DONE

			##############################
			# Gather GENERAL data
			##############################
			if not self.evol:
				#at this stage we should have exactly one solution
				if len(allSamples) != 1 :
					raise Error('something went wrong')
				stats['CON_num_rm'] = len(parsed_cons)
				stats['CON_sat_num_rm'] = len(parsed_cons) - sum(numVioMap[allSamples[0]])
				stats['CON_sat_%_rm'] = -1 if len(parsed_cons) == 0 else stats['CON_sat_num_rm'] / len(parsed_cons)
				stats['CON_rm_vals'] = allVals[allSamples[0]]
			else:
				stats['restarts'] = restarts
				num_cons = len(parsed_cons)
				stats['CON_num'] = num_cons
				stats['CON_num_hard'] = num_hard_cons
				num_soft_cons = len(parsed_cons) - num_hard_cons
				stats['CON_num_soft'] = num_soft_cons
				
				allSolStats = {}
				if measurement_outputs:
					bestGlobal = allSamples[sortedGlobal[0][-1]]
					allSamples = [bestGlobal]
					names = ['sol_best_global']
				else:
					names = [f'sol-{i}' for i in range(len(allSamples))]
					
				for i in range(len(allSamples)):
					sol = allSamples[i]						
					solStats = {}
					solNumVioHard, solNumVioSoft = numVioMap[sol]
					solStats['CON_sat_num'] = num_cons - solNumVioHard - solNumVioSoft
					solStats['CON_sat_%'] = -1 if num_cons == 0 else solStats['CON_sat_num'] / num_cons
					solStats['CON_sat_num_hard'] = num_hard_cons - solNumVioHard
					solStats['CON_sat_%_hard'] = -1 if num_hard_cons == 0 else solStats['CON_sat_num_hard'] / num_hard_cons
					solStats['CON_sat_num_soft'] = num_soft_cons - solNumVioSoft
					solStats['CON_sat_%_soft'] = -1 if num_soft_cons == 0 else solStats['CON_sat_num_soft'] / num_soft_cons
					solStats['CON_vals'] = allVals[sol]

					allSolStats[names[i]] = solStats					

				stats['solutions'] = allSolStats

				##############################
				# Gather HISTORY data
				##############################
				historyStats = []
				for historicSolSet in reversed(historicSolSets):
					# for a solution set at a given time stamp
					# get historic solutions as samples:
					historicSamples = []
					historicFs = []

					t = historicSolSet[0]
					hist_sol_x = historicSolSet[1].X
					hist_sol_f = historicSolSet[1].F
					if len(hist_sol_x.shape) == 1:
						# handling of GA
						hist_sol_x = [hist_sol_x]
						hist_sol_f = [hist_sol_f]

					for sol_id, historicSol in enumerate(hist_sol_x):
						utils.fillSample(self, historicSol)
						historicFs.append(hist_sol_f[sol_id])
						found = False
						while not found:
							try:
								historicSamples.append(Samplable.sampleAll(self.dependencies))
								found = True
							except:
								print('failed to sample - history')

					# ANALYSIS: historicFs and historicSamples
					# Find sol with lowest total F
					_, sh_heu_tot, _ = self.analyseFset(heuristicTargets, historicFs)

					# Handle consraint vals of solutions
					allVals, numVioMap, sortedGlobal, sortedHardPrio = self.analyseSolSet(parsed_cons, historicSamples)
					
					allSolStats = {}
					if measurement_outputs:
						allSolStats['time'] = t
						if save_history == 'shallow':
							# def storeData(num_vio, heu_val, best_id):
							# 	data = {}
							# 	data['CON_sat_num'] = num_cons - num_vio
							# 	# data['CON_sat_%'] = ( num_cons - num_vio) / num_cons
							# 	data['heu_val_tot'] = heu_val
							# 	data['heu_val_all'] = list(historicFs[best_id])
							# 	return data
							
							allSolStats['least_con_vio'] = min(sortedGlobal, key = lambda x: x[0])[0]
							allSolStats['gd'] = GD(heuristicTargets).do(historicSolSet[1].F)
							allSolStats['igd'] = IGD(heuristicTargets).do(historicSolSet[1].F)
							allSolStats['min_f_sum'] = sh_heu_tot
							
							# sortedGlobal.sort(key = lambda x: x[1])
							# allSolStats['CON_violations_num'] = [i[0] for i in sortedGlobal]
							# allSolStats['F'] = [list(i) for i in historicFs]
						
						elif save_history == 'deep':
							# Best global solution
							sol = historicSamples[sortedGlobal[0][-1]]
							solNumVioHard, solNumVioSoft = numVioMap[sol]
							allSolStats['CON_sat_num'] = num_cons - solNumVioHard - solNumVioSoft
							allSolStats['CON_sat_%'] = allSolStats['CON_sat_num'] / num_cons
							allSolStats['CON_sat_num_hard'] = num_hard_cons - solNumVioHard
							allSolStats['CON_sat_%_hard'] = allSolStats['CON_sat_num_hard'] / num_hard_cons
							allSolStats['CON_sat_num_soft'] = num_soft_cons - solNumVioSoft
							allSolStats['CON_sat_%_soft'] = allSolStats['CON_sat_num_soft'] / num_soft_cons
							allSolStats['CON_vals'] = allVals[sol]

						historyStats.append(allSolStats)

				stats['history'] = historyStats
			
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
				if c.tgt != -1 and type(c.tgt) is not str:
					vj = sample[self.objects[c.tgt]]

				if c.type == Cstr_type.ONROAD:
            		# TODO ONROAD is temporarily kept, but should be phased out
					vals[str(c)] = vi.containedHeuristic(self.network.drivableRegion)
					if vals[str(c)] != 0 : numVioHard += 1
					# num_hard_cons += 1
				if c.type == Cstr_type.ONREGIONTYPE:
					container = utils.type2region(Scenario, c.tgt, vi)
					vals[str(c)] = vi.containedHeuristic(container)
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
	
	def analyseFset(self, targetHeuristics, allFs):
		heu_totals = []
		for i_fs in allFs:
			assert len(targetHeuristics) == len(i_fs)
			total_heu_val = 0
			for heu_i in range(len(i_fs)):
				heu_v = i_fs[heu_i]
				heu_max = targetHeuristics[heu_i]
				diff = heu_v - heu_max
				if diff > 0:
					total_heu_val += diff
			heu_totals.append(total_heu_val)

		return min(range(len(heu_totals)), key=lambda x : heu_totals[x]), min(heu_totals), heu_totals


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
