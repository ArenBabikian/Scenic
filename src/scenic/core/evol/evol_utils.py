
from scenic.core.evol.constraints import Cstr_type
from scenic.core.evol.nsga2mod import NSGA2M
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.soo.nonconvex.es import ES
from pymoo.algorithms.soo.nonconvex.ga import GA

from pymoo.util.termination.collection import TerminationCollection
from pymoo.util.termination.max_time import TimeBasedTermination
from scenic.core.evol.OneSolutionHeuristicTermination import OneSolutionHeuristicTermination

from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

import os


def getMapBoundaries(params, num_obj):
    map_name = os.path.basename(params.get('map'))
    bounds = []
    if map_name == "town02.xodr":
        bounds = [-15, -315, 200, -98]
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
            'nsga2': ['categories', 'actors', 'importance'],
            'nsga3': ['categories', 'actors', 'none']}

def getAlgo(params):
    algo_name = params.get('evol-algo')
    restart = float(params.get('evol-restart-time'))
    if algo_name == 'nsga2':        
        algorithm = NSGA2M(pop_size=20, n_offsprings=10, restart_time=restart,
                           eliminate_duplicates=True)
    elif algo_name == 'ga':
        algorithm = GA(pop_size=20, n_offsprings=10, restart_time=restart,
                       eliminate_duplicates=True)
    elif algo_name == 'nsga3':
        algorithm = NSGA3(pop_size=20, n_offsprings=10, restart_time=restart,
                          eliminate_duplicates=True)
        
        # algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)
    else:
        raise Exception(f'Evol algo <{algo_name}> is unknown.')
    
    # validate objective approach
    obj_def = params.get('evol-obj')
    if obj_def not in ALGO2OBJ[algo_name]:
        raise Exception(f'Invalid objective functions <{obj_def}> for algo <{algo_name}>.')

    return algorithm

def getHeuristic(scenario, x, constraints):
    objects = scenario.objects
    obj_def = scenario.params.get('evol-obj')

    # GET Constraint2ObjectiveFunctionId    
    # obj_funcs is currently hardcoded
    con2id = []
    if obj_def == 'one':
        con2id = [0 for _ in constraints]
        obj_funcs = [0]
        exp = [1]
    elif obj_def == 'categories':
        con2id = [int(c.type.value/10) for c in constraints]
        obj_funcs = [0, 0, 0, 0, 0]
        exp = [3, 3, 2, 2, 2]
    elif obj_def == 'actors':
        con2id = [c.src for c in constraints]
        obj_funcs = [0 for _ in range(len(objects))]
        exp = [1 for _ in range(len(objects))]
    elif obj_def == 'importance':
        con2id = [int(c.type.value >= 20) for c in constraints]
        obj_funcs = [0, 0]
        exp = [1, 1]
    elif obj_def == 'none':
        con2id = [i for i in range(len(constraints))]
        obj_funcs = [0 for _ in range(len(constraints))]
        exp = [1 for _ in range(len(constraints))]

    #     fun = [(lambda x:x**3),
    #         (lambda x:x**3),
    #         (lambda x:x**2),
    #         (lambda x:x**2),
    #         (lambda x:x**2)]

    # return a 3-item list [distance from visibility, travel distance to avoid intersection, distance from contained region]
    # x = [  97.64237302, -236.70268295,  -14.74759737,  -98.51499928,   -5.88366596, -109.51614019,   -7.30336197,  -99.24476481]
    scenario.fillSample(x)

    ## GET HEURISTIC VALUES
    ## Assuming that ego position in actor llist does not change
    for c_id, c in enumerate(constraints):
        vi = objects[c.src]
        vj = None
        if c.tgt != -1:
            vj = objects[c.tgt]
        heu_val = 0
        
        # Constraints Switch
        if c.type == Cstr_type.ONROAD:
            ### How far is the farthest corner of vi from a valid region that can contain it?
            container = scenario.containerOfObject(vi)
            heu_val = vi.containedHeuristic(container)
        if c.type == Cstr_type.NOCOLLISION:
            ### Are vi and vj intersecting?
            if vi.intersects(vj):
                heu_val = 10
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

        obj_funcs[con2id[c_id]] += heu_val

    out = [of**exp[i] for i, of in enumerate(obj_funcs)]
    # out = [exp[i](of) for i, of in enumerate(obj_funcs)]
    return out


def getProblem(scenario, constraints):

    objects = scenario.objects
    tot_var = len(objects)*2

    # MAP BOUNDARIES
    loBd, hiBd = getMapBoundaries(scenario.params, len(objects))

    # PROBLEM
    class MyProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=tot_var, n_obj=5, n_constr=0,
                            xl=loBd, xu=hiBd)

        # Notes: x = [x_a0, y_a0, x_a1, y_a1, ...]
        def _evaluate(self, x, out, *args, **kwargs):
            # TODO
            heuristics = getHeuristic(scenario, x, constraints)
            # out["G"] = heuristics[:2]
            # out["F"] = heuristics[2:]
            out["F"] = heuristics
    return MyProblem()


def getTermination(timeout):
    # TODO
    t1 = OneSolutionHeuristicTermination(heu_vals=[0, 0, 0, 0, 0])
    # TEMP
    # t1 = MultiObjectiveSpaceToleranceTermination(tol=0.0025, n_last=30)	
    # t1 = ConstraintViolationToleranceTermination(n_last=20, tol=1e-6,)	
    # t1 = IGDTermination	
    t2 = TimeBasedTermination(max_time=timeout)
    termination = TerminationCollection(t1, t2)
    return termination


def getEvolNDSs(scenario, constraints, verbosity):

    # GET ALGORITHM
    algorithm = getAlgo(scenario.params)

    # GET PROBLEM
    problem = getProblem(scenario, constraints)

    # GET TERMINATION
    termination = getTermination(scenario.timeout)

    # RUN PROBLEM
    res = minimize(problem, algorithm, termination, save_history=True, verbose=(verbosity > 1), seed=1)
    # (For Repeatability) use seed=1 option
    return res
