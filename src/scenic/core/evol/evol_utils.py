
from scenic.core.evol.constraints import Cstr_type

from pymoo.util.termination.collection import TerminationCollection
from pymoo.util.termination.max_time import TimeBasedTermination
from scenic.core.evol.OneSolutionHeuristicTermination import OneSolutionHeuristicTermination
from scenic.core.vectors import Vector

from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

import os

from scenic.core.evol.geneticModAlgo import NSGA2MOD, NSGA3MOD, GAMOD
import scenic.core.evol.heuristics as heu_utils
from scenic.domains.driving.roads import _toVector

def getMapBoundaries(params, num_obj):

    # TODO dynamically determine map borders based on coordinates
    # TODO particularly relevant for intersections being tested

    map_name = os.path.basename(params.get('map'))
    bounds = []
    # [loX, loY, hiX, hiY]
    if map_name == "town02.xodr":
        bounds = [-15, -315, 200, -98]
    if map_name == "town05.xodr":
        # TENTATIVELY focus only on an intersection
        bounds = [-31, -72, 71, 78]
        bounds = [16, -13, 43, 13] # inside the intersection
    elif map_name == "town10HD.xodr":
        bounds = [-126, -151, 121, 80]
    elif map_name == "tram05.xodr":
        bounds = [-155, -101, 103, 80]
    elif map_name == "tram05-mod.xodr":
        bounds = [-140, -160, 215, 70]
    elif map_name == "zalaFullcrop.xodr":
        bounds = [-59, 1337, 211, 1811] # full smart-city section
        # bounds = [-59, 211, 1337, 1811] # smaller version
    else:
        raise Exception(f'Map <{map_name}> is unknown to NSGA')
    loBd, hiBd = [], []
    for _ in range(num_obj):
        # TODO currently hard-coded wrt. the map
        loBd.extend(bounds[:2])
        hiBd.extend(bounds[2:])

    return loBd, hiBd

ALGO2OBJ = {'ga':['one'],
            'nsga2': ['actors', 'importance', 'categImpo'],
            'nsga3': ['categories', 'none', 'categImpo', 'actors']}

def getAlgo(params, n_objectives):
    algo_name = params.get('evol-algo')
    restart_raw = params.get('evol-restart-time')
    restart = float(restart_raw if restart_raw else -1)
    if algo_name == 'nsga2':
        algorithm = NSGA2MOD(pop_size=5, n_offsprings=None, restart_time=restart,
                           eliminate_duplicates=True)
    elif algo_name == 'ga':
        from pymoo.algorithms.soo.nonconvex.ga import GA
        algorithm = GAMOD(pop_size=5, n_offsprings=None, restart_time=restart,
                       eliminate_duplicates=True)
    elif algo_name == 'nsga3':
        from pymoo.factory import get_reference_directions
        # TODO analyse n_partitions
        ref_dirs = get_reference_directions("das-dennis", n_dim=n_objectives, n_partitions=1)
        algorithm = NSGA3MOD(ref_dirs=ref_dirs, pop_size=None, n_offsprings=None, restart_time=restart,
                          eliminate_duplicates=True)
        
        # algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)
    else:
        raise Exception(f'Evol algo <{algo_name}> is unknown.')

    return algorithm


def handleConstraints(scenario, constraints):
    objects = scenario.objects
    obj_def = scenario.params.get('evol-obj')
    
    # validate objective approach
    algo_name = scenario.params.get('evol-algo')
    if obj_def not in ALGO2OBJ[algo_name]:
        raise Exception(f'Invalid objective functions <{obj_def}> for algo <{algo_name}>.')

    # GET Constraint2ObjectiveFunctionId    
    # obj_funcs is currently hardcoded
    # exp may be generalised to any function
    # fun = [(lambda x:x**3), (lambda x:x**3), (lambda x:x**2), (lambda x:x**2), (lambda x:x**2)]
    if obj_def == 'one':
        con2id = [0 for _ in constraints]
        exp = [1]
    elif obj_def == 'categories':
        con2id = [int(c.type.value/10) for c in constraints]
        exp = [1, 1, 1, 1, 1, 1]
    elif obj_def == 'actors':
        con2id = [c.src for c in constraints]
        exp = [1 for _ in range(len(objects))]
    elif obj_def == 'importance':
        con2id = [int(c.type.value >= 20) for c in constraints]
        exp = [3, 2]
    elif obj_def == 'categImpo':
        con2id = [int(c.type.value/10) for c in constraints]
        exp = [3, 3, 2, 2, 2, 3]
    elif obj_def == 'none':
        con2id = [i for i in range(len(constraints))]
        exp = [1 for _ in range(len(constraints))]

    return con2id, exp


def type2region(scenario, regionType, vi):
    network = scenario.network
    TYPE2REGION = {
        'default': scenario.containerOfObject(vi), # Default region wrt. actor type
        'drivable': network.drivableRegion, # All lanes union all intersections.
        'walkable': network.walkableRegion, # All sidewalks union all crossings.
        'road': network.roadRegion, # All roads (not part of an intersection).
        'lane': network.laneRegion, # All lanes
        'intersection': network.intersectionRegion, # All intersections.
        'crossing': network.crossingRegion, # All pedestrian crossings.
        'sidewalk': network.sidewalkRegion, # All sidewalks
        'curb': network.curbRegion, # All curbs of ordinary roads.
        'shoulder': network.shoulderRegion # All shoulders (by default, includes parking lanes).
    }

    if regionType not in TYPE2REGION:
        raise Exception(f'Unhandled region type <{regionType}>')

    container = TYPE2REGION[regionType]
    if container is None:
        raise Exception(f'Container for region type <{regionType}> is None')

    return container

def findClosestWaypoint(scenario, point, assignedManeuver=None):
    
    assert scenario.testedIntersection is not None, "WaypointSnapping only suported for intersection testing (for now)"

    # 0. to avoid prioriting for a targetted maneuver, set assignedManeuver=None

    # 1. find connaectingRoads it is potentially on
    all_possible_maneuvers = scenario.testedIntersection.maneuversAt(point)
    all_possible_lanes = [m.connectingLane for m in all_possible_maneuvers]

    # 2. for each connecting road, find closest point (and distance to) on centerline
    if len(all_possible_lanes) == 0:
        return point, None, 0

    curDistToClosestPoint = float('inf')
    closestPoint = point
    m, h = None, 0

    for i, lane in enumerate(all_possible_lanes):
        m = all_possible_maneuvers[i].type
        cl = lane.centerline
        d = cl.distanceTo(point)
        # Assign best point
        if d < curDistToClosestPoint and (assignedManeuver == None or assignedManeuver == m):
            curDistToClosestPoint = d
            proj = cl.project(point)
            closestPoint = Vector(proj.x, proj.y)
            h_raw = lane.orientation[closestPoint]
            h = 0 if h_raw == None else h_raw

    return closestPoint, m, h


def fillSample(scenario, coords):
    for i, vi in enumerate(scenario.objects):

        # Notes: coords = [x_a0, y_a0, x_a1, y_a1, ...]
        val_x = coords[2*i]
        val_y = coords[2*i + 1]
        v = Vector(val_x, val_y)

        assignedManeuver = None if i not in scenario.actorIdsWithManeuver else scenario.actorIdsWithManeuver[i]
        
        if i in scenario.actorIdsSnappedToWayPoint:
            #     WAYPOINT, NOT MANEUVER
            # (places position to closest waypoint, and assigns corresponding heading. If not on a lane, returns same point and heading 0)
            #     WAYPOINT,     MANEUVER
            # (places position to closest waypoint on lane which allows corresponding maneuevr, and assigns corresponding heading)
            v, maneuver, heading = findClosestWaypoint(scenario, v, assignedManeuver)
        else:
            # (keep point as is)
            if assignedManeuver != None:

                # NOT WAYPOINT,     MANEUVER
                # (Default heading if in a positin where the assigned maneuever is not possible. Otherwise, assign the correct heading)

                all_possible_maneuvers = scenario.testedIntersection.maneuversAt(v)
                all_possible_maneuvers[:] = [m for m in all_possible_maneuvers if m.type == assignedManeuver]
                all_possible_orientations = [m.connectingLane.orientation[v] for m in all_possible_maneuvers]

                heading  = scenario.network._defaultRoadDirection(v) if len(all_possible_orientations) == 0 \
                    else all_possible_orientations[0]

            else:
                # NOT WAYPOINT, NOT MANEUVER 
                # (keep point as is, assigns default heading at point)
                heading = scenario.network._defaultRoadDirection(v)

        vi.position = v
        vi.heading = heading


def getHeuristic(scenario, x, constraints, con2id, exp):
    objects = scenario.objects

    obj_funcs = [0 for _ in range(len(exp))]
    fillSample(scenario, x)

    ## GET HEURISTIC VALUES
    ## Assuming that ego position in actor list does not change
    for c_id, c in enumerate(constraints):
        vi = objects[c.src]
        vj = None
        if c.tgt != -1 and type(c.tgt) is not str:
            vj = objects[c.tgt]
        heu_val = 0
        
        # Constraints Switch
        if c.type == Cstr_type.ONROAD:
            # TODO ONROAD is temporarily kept, but should be phased out
            ### How far is the farthest corner of vi from a valid region that can contain it?
            container = scenario.network.drivableRegion
            heu_val = vi.containedHeuristic(container)
        if c.type == Cstr_type.ONREGIONTYPE:
            container = type2region(scenario, c.tgt, vi)
            heu_val = vi.containedHeuristic(container)

        if c.type == Cstr_type.NOCOLLISION:
            ### Are vi and vj intersecting?
            if vi.intersects(vj):
                heu_val = 10
        if c.type == Cstr_type.NOTONSAMEROAD:
            heu_val = heu_utils.heuristic_notOnSameRoad(scenario, vi, vj)

        if c.type == Cstr_type.CANSEE:
            ### How far is vj from being visible wrt. to vi?
            heu_val = vi.canSeeHeuristic(vj)

        if c.type == Cstr_type.HASTOLEFT:
            heu_val = vi.toLeftHeuristic(vj)
        if c.type == Cstr_type.HASTORIGHT:
            heu_val = vi.toRightHeuristic(vj)
        if c.type == Cstr_type.HASBEHIND:
            heu_val = vi.behindHeuristic(vj)
        if c.type == Cstr_type.HASINFRONT:
            heu_val = vi.inFrontHeuristic(vj)

        if c.type == Cstr_type.DISTCLOSE:
            heu_val = vi.distCloseHeuristic(vj)
        if c.type == Cstr_type.DISTMED:
            heu_val = vi.distMedHeuristic(vj)
        if c.type == Cstr_type.DISTFAR:
            heu_val = vi.distFarHeuristic(vj)

        if c.type == Cstr_type.COLLIDESATMANEUVER:
            maneuver_name = c.tgt
            heu_val = heu_utils.heuristic_collidesAtManeuver(vi, maneuver_name, scenario)

        if c.type == Cstr_type.DOINGMANEUVER:
            maneuver_name = c.tgt
            heu_val = heu_utils.heuristic_doingManeuver(vi, maneuver_name, scenario)

        obj_funcs[con2id[c_id]] += heu_val

    out = [of**exp[i] for i, of in enumerate(obj_funcs)]
    # out = [exp[i](of) for i, of in enumerate(obj_funcs)]
    return out


def getProblem(scenario, constraints):

    objects = scenario.objects
    tot_var = len(objects)*2

    # MAP BOUNDARIES
    loBd, hiBd = getMapBoundaries(scenario.params, len(objects))

    # HANDLE CONSTRAINT CATEGORIZATION
    con2id, exp = handleConstraints(scenario, constraints)

    # PROBLEM
    class MyProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=tot_var, n_obj=len(exp), n_constr=0,
                            xl=loBd, xu=hiBd)

        # Notes: x = [x_a0, y_a0, x_a1, y_a1, ...]
        def _evaluate(self, x, out, *args, **kwargs):
            # TODO
            heuristics = getHeuristic(scenario, x, constraints, con2id, exp)
            # out["G"] = heuristics[:2]
            # out["F"] = heuristics[2:]
            out["F"] = heuristics
    return MyProblem(), len(exp)


def getTermination(target_heuristic_values, timeout):
    # TODO
    t1 = OneSolutionHeuristicTermination(heu_vals=target_heuristic_values)
    # TEMP
    # t1 = MultiObjectiveSpaceToleranceTermination(tol=0.0025, n_last=30)	
    # t1 = ConstraintViolationToleranceTermination(n_last=20, tol=1e-6,)	
    # t1 = IGDTermination	
    t2 = TimeBasedTermination(max_time=timeout)
    termination = TerminationCollection(t1, t2)
    return termination


def validateHistory(params):
    history = params.get('evol-history')
    if history not in ['none', 'shallow', 'deep']:
        raise Exception(f'Evol History spec <{history}> is invalid.')
    return None if history == 'none' else history


def getEvolNDSs(scenario, constraints, verbosity):

    # GET PROBLEM
    problem, num_objectives = getProblem(scenario, constraints)

    # GET ALGORITHM
    algorithm = getAlgo(scenario.params, num_objectives)

    # GET TERMINATION
    target_heuristic_values = [0 for _ in range(num_objectives)]
    termination = getTermination(target_heuristic_values, scenario.timeout)

    # VALIDATE HISTORY
    history = validateHistory(scenario.params)

    # RUN PROBLEM
    # (For Repeatability) use seed=1 option
    res = minimize(problem, algorithm, termination, save_history=history, verbose=(verbosity > 1))
    return res, target_heuristic_values
