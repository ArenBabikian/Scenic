# TODO delete
# This file has become obsolete

# import importlib_metadata as metadata
import argparse
from ast import parse
from pymoo.algorithms.moo.nsga3 import NSGA3
import scenic.syntax.translator as translator
import scenic.core.errors as errors

import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.problems.functional import FunctionalProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.factory import get_sampling, get_crossover, get_mutation, get_termination
from pymoo.optimize import minimize

import time
import io
import tempfile
import os
import gc
import subprocess

def createScenicStr(x):
    return f"""param map = localPath(\'C:/git/CarlaScenarioGen/Interface/maps/CARLA/Town02.xodr\')
model scenic.simulators.carla.model
p_ego = {x[0]} @ {x[1]}
ego = Car at p_ego, with color[188/256, 185/256, 183/256] # Silver
p_a = {x[2]} @ {x[3]}
a = Car at p_a, with requireVisible True
# require(p_a ahead of p_ego)
"""

def createScenicFile(x):
    scenicText = createScenicStr(x)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.scenic', mode="w+")
    if translator.verbosity >= 1:
        print(f'    Created temporary file at {tmp.name}')
    tmp.write(scenicText)
    tmp.close
    tmp.seek(0)
    return tmp

def callScenic(x, v=0):
    scenicStr = createScenicStr(x)

    translator.verbosity = v
    params = {}
    params['heuristic'] = True
    params['no-validation'] = True
    errors.showInternalBacktrace = True

    # Load scenario from file
    if translator.verbosity >= 1:
        print('Beginning scenario construction...')

    startTime = time.time()
    # TODO we can probably find a way to avoid writing to a string
    scenario = errors.callBeginningScenicTrace(
        lambda: translator.scenarioFromString(scenicStr, params=params)
    )
    totalTime = time.time() - startTime
    
    if translator.verbosity >= 1:
        print(f'Scenario constructed in {totalTime:.2f} seconds.')
    return scenario

def getHeuristic(x, v=0):
    scenario = callScenic(x, v)
    return scenario.heuristic

def getArgs():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--iterations', '-i', help='number of iterations',
                     type=int, default=5, metavar='N')

    return parser.parse_args()

class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=4,
                         n_obj=3,
                         n_constr=0,
                         xl=np.array([-15, -315, -15, -315]),
                         xu=np.array([200, -98, 200, -98]))

    # Notes
    # x[0] = x_ego
    # x[1] = y_ego
    # x[2] = x_oth
    # x[3] = y_oth

    def _evaluate(self, x, out, *args, **kwargs):
        # function to optimize
        # f1 = getHeuristic(x)[0]
        # f1 = (x[0]-1)**2 + x[1]**2

        # constraints
        # g1 = 2*(x[0]-0.1) * (x[0]-0.9) / 0.18
        # g2 = - 20*(x[0]-0.4) * (x[0]-0.6) / 4.8

        # out["F"] = [f1]
        # out["G"] = [] #[g1, g2]
        out["F"] = getHeuristic(x)

def str2list(st):
    return st[1:-1].split()

def render(st, v=0):    
    tmp = createScenicFile(str2list(st))
    print(tmp.name)
    process = subprocess.Popen(['poetry', 'run', 'scenic',
                        '-b', '-p', 'no-validation', 'True',
                        '--count', '1', '-v', str(v), tmp.name],
                        shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    if v > 0:
        stdout, stderr = process.communicate()
        print('OUT')
        print(stdout.decode('utf-8'))
        print('ERR')
        print(stderr.decode('utf-8'))
    return process, tmp

#### EXECUTION
def main():
    args = getArgs()
    translator.verbosity = 0

    print("--Running NSGA--")   
    problem = MyProblem()
    # algorithm = GA(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
    algorithm = NSGA2(pop_size=20, n_offsprings=10, eliminate_duplicates=True)
    # algorithm = NSGA3(ref_dirs=X, pop_size=20, n_offsprings=10)

    termination = get_termination("n_gen", args.iterations)
    res = minimize(problem, algorithm, termination,
                seed=1, save_history=True, verbose=True)

    print("--Results--")
    print(res.X)
    print(res.F)
    
    print('--Rendering--')
    tmpFiles = []
    processes = []
    for sol in list(res.X):
        p, t = render(str(sol))
        processes.append(p)
        tmpFiles.append(t)

    for proc in processes:
        proc.wait()

    print('--Closing--')
    for tmp in tmpFiles:
        tmp.close()
        os.unlink(tmp.name)

    # import matplotlib.pyplot as plt
    # xl, xu = problem.bounds()
    # plt.figure(figsize=(7, 5))
    # plt.scatter(X[:, 0], X[:, 1], s=30, facecolors='none', edgecolors='r')
    # plt.xlim(xl[0], xu[0])
    # plt.ylim(xl[1], xu[1])
    # plt.title("Design Space")
    # plt.show()

    # plt.figure(figsize=(7, 5))
    # plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
    # plt.title("Objective Space")
    # plt.show()

def test(st, v=0):
    startTime = time.time()
    h = getHeuristic(str2list(st), v)
    totalTime = time.time() - startTime
    print(h)
    print(f'time: {totalTime}')

if __name__ == "__main__":
    # NOTES:
    # With text+temp file creation+parsing, one run of getting the heuristic values takes about 0.53 seconds
    # With text+parsing, the time is comparable.
    # TODO get rid of parsing and create objects directly??

    # main()
    # for i in range(1):
    #     test("[ 2.41825379e+01 -1.87883487e+02 -3.52244892e+00 -1.70315190e+02]", v=3)
    #     gc.collect()
    x = ['[  184.91764775 -189.44697598  179.23141179 -187.46458814]',
 '[  185.15287479 -189.44697598  179.23141179 -187.58738823]',
 '[  189.74796814 -133.31806774  190.2316076  -146.33830813]']
    for i in x:
        render(i)
    # render('[  15.31489524 -170.73699369  -6.31487594 -165.55344661]')
