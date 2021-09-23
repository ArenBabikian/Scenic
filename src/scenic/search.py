# import importlib_metadata as metadata
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

def createScenicTemp(x):
    scenicText = f"""param map = localPath(\'C:/git/CarlaScenarioGen/Interface/maps/CARLA/Town02.xodr\')
model scenic.simulators.carla.model

ego = Car at {x[0]} @ {x[1]}, with color[188/256, 185/256, 183/256] # Silver
a = Car at {x[2]} @ {x[3]}, with requireVisible True
"""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.scenic', mode="w+")
    if translator.verbosity >= 1:
        print(f'    Created temporary file at {tmp.name}')
    tmp.write(scenicText)
    tmp.close
    tmp.seek(0)
    return tmp

def callScenic(tmp):
    translator.verbosity = 0

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
        lambda: translator.scenarioFromFile(tmp.name, params=params)
    )
    totalTime = time.time() - startTime
    
    if translator.verbosity >= 1:
        print(f'Scenario constructed in {totalTime:.2f} seconds.')
    return scenario

def getHeuristic(x):
    tmp = createScenicTemp(x)
    scenario = callScenic(tmp)
    tmp.close()
    os.unlink(tmp.name)
    return scenario.heuristic
    # currently, there is a memory link issue, we would need to delete the tmp file
    # else:
    #     os.unlink(tmp.name)


class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=4,
                         n_obj=3,
                         n_constr=0,
                         xl=np.array([-15, -315, -15, -315]),
                         xu=np.array([200, -98, 200, -98]))

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


#### EXECUTION
def main():

    translator.verbosity = 0
    
    problem = MyProblem()
    # algorithm = GA(pop_size=20,
    #     n_offsprings=10,
    #     eliminate_duplicates=True)
    algorithm = NSGA2(
        pop_size=20,
        n_offsprings=10,
        eliminate_duplicates=True
    )
    # algorithm = NSGA3(ref_dirs=X,
    #     pop_size=20,
    #     n_offsprings=10)
    # )

    termination = get_termination("n_gen", 40)
    res = minimize(problem,
                algorithm,
                termination,
                seed=1,
                save_history=True,
                verbose=True)

    print("--Results--")
    print(res.X)
    print(res.F)
    return res.X

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

def str2list(str):
    return str[3:-1].split()

def test(str):

    print(getHeuristic(str2list(str)))

def render(str):    
    tmp = createScenicTemp(str2list(str))
    print(tmp.name)
    import subprocess
    process = subprocess.Popen(['poetry', 'run', 'scenic',
                        '-b', '-p', 'no-validation', 'True',
                        '--count', '1', tmp.name],
                        shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    # stdout, stderr = process.communicate()
    # print(stdout)
    # print(stderr)
    return process, tmp

if __name__ == "__main__":
    sol = main()
    print('--rendering--')
    tmpFiles = []
    processes = []
    for s in list(sol):
        p, t = render(str(s))
        processes.append(p)
        tmpFiles.append(t)

    for proc in processes:
        proc.wait()
    
    for tmp in tmpFiles:
        tmp.close()
        os.unlink(tmp.name)

    # render("[ 2.41825379e+01 -1.87883487e+02 -3.52244892e+00 -1.70315190e+02]")
