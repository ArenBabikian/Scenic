from scenic.core.evol.constraints import Cstr_type, Cstr
import random
from sat import *
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score

regionTypeNames = [
    'default', # Default region wrt. actor type
    'drivable', # All lanes union all intersections.
    'walkable', # All sidewalks union all crossings.
    'road', # All roads (not part of an intersection).
    'lane', # All lanes
    'intersection', # All intersections.
    'crossing', # All pedestrian crossings.
    'sidewalk', # All sidewalks
    'curb', # All curbs of ordinary roads.
    'shoulder'
]

def generateNConstraints(num, unsat):
	constraintsList = []
	objectsList = []
	objectsIdx = -1
	while len(constraintsList) < num:
		objectsIdx += 1
		objectsList.append(f'obj{objectsIdx}')
		regionType = random.choice(regionTypeNames)
		constraintsList.append(Cstr(Cstr_type.ONREGIONTYPE, objectsList[objectsIdx], regionType))
		if (regionType in {'drivable', 'road', 'lane', 'intersection'}):
			constraintsList.append(Cstr(Cstr_type.ONROAD, objectsList[objectsIdx], '-1'))
		if unsat:
			constraintsList.append(Cstr(Cstr_type.ONREGIONTYPE, objectsList[objectsIdx], 'intersection'))
			constraintsList.append(Cstr(Cstr_type.ONREGIONTYPE, objectsList[objectsIdx], 'sidewalk'))
		positions = [Cstr_type.HASTOLEFT, Cstr_type.HASTORIGHT, Cstr_type.HASBEHIND, Cstr_type.HASINFRONT]
		distances = [Cstr_type.DISTCLOSE, Cstr_type.DISTMED, Cstr_type.DISTFAR]
		for i in range(0, objectsIdx):
			position = random.choice(positions)
			distance = random.choice(distances)
			constraintsList.append(Cstr(distance, objectsList[objectsIdx], objectsList[i]))
			constraintsList.append(Cstr(distance, objectsList[i], objectsList[objectsIdx]))
			constraintsList.append(Cstr(position, objectsList[i], objectsList[objectsIdx]))
			constraintsList.append(Cstr(position, objectsList[objectsIdx], objectsList[i]))
			constraintsList.append(Cstr(Cstr_type.CANSEE, objectsList[objectsIdx], objectsList[i]))
			constraintsList.append(Cstr(Cstr_type.NOCOLLISION, objectsList[objectsIdx], objectsList[i]))
	return constraintsList[:num]

# Returns time in miliseconds used to evaluate N constraints
def getRuntimeForConstraints(constraints):
	start = time.time()
	satResults = validate_sat(constraints)
	stop = time.time()
	if not satResults:
		print(f"Run with {len(constraints)} constraints not satisfied\n")
	return (stop - start)*1000

def runTests(maxNum, runs, unsat):
	listOfConstraintsLists = []
	for i in range(0, runs):
		listOfConstraintsLists.append(generateNConstraints(maxNum + 10, unsat))
	xvals = []
	yvals = []
	for i in range(1, maxNum + 1):
		xvals.append(i)
		runtimes = []
		for constraintsList in listOfConstraintsLists:
			runtimes.append(getRuntimeForConstraints(constraintsList[:i]))
		runtime = sum(runtimes) / len(runtimes)
		yvals.append(runtime)
		print(f"Obtained runtime of {runtime} for {i} out of {maxNum}\n")
	plt.scatter(xvals, yvals)
	plt.legend(loc='upper left')
	if unsat:
		plt.title("Z3 Solver runtime for varying numbers of constraints, constraints not satisfiable")
	else:
		plt.title("Z3 Solver runtime for varying numbers of constraints, constraints satisfiable")
	plt.xlabel("Number of constraints")
	plt.ylabel(f"Average runtime of {runs} runs (ms)")
	z = np.polyfit(xvals, yvals, 1)
	p = np.poly1d(z)
	# Equation of the line
	equation = f"y={z[0]:.2f}x + {z[1]:.2f}"
	r_squared = r2_score(yvals, p(xvals))
	plt.annotate(f"{equation}\n r^2 = {r_squared:.2f}", xy=(0.05, 0.85), xycoords='axes fraction', fontsize=10)
	plt.plot(xvals, p(xvals))
	plt.show()

def runTestsComparison(maxNum, runs):
	listOfConstraintsListsUnsat = []
	listOfConstraintsListsSat = []
	for i in range(0, runs):
		listOfConstraintsListsUnsat.append(generateNConstraints(maxNum + 10, True))
		listOfConstraintsListsSat.append(generateNConstraints(maxNum + 10, False))
	xvals = []
	
	yvalsSat = []
	yvalsUnsat = []
	for i in range(1, maxNum + 1):
		xvals.append(i)
		satRuntimes = []
		unsatRuntimes = []
		for constraintsList in listOfConstraintsListsSat:
			satRuntimes.append(getRuntimeForConstraints(constraintsList[:i]))
		for constraintsList in listOfConstraintsListsUnsat:
			unsatRuntimes.append(getRuntimeForConstraints(constraintsList[:i]))
		satRuntime = sum(satRuntimes) / len(satRuntimes)
		unsatRuntime = sum(unsatRuntimes) / len(unsatRuntimes)
		yvalsSat.append(satRuntime)
		yvalsUnsat.append(unsatRuntime)
		print(f"Obtained runtime of {satRuntime}, {unsatRuntime} for {i} out of {maxNum}\n")
	plt.scatter(xvals, yvalsSat, c="b", label="Satisfiable")
	plt.scatter(xvals, yvalsUnsat, c="r", label="Unsatisfiable")
	plt.legend(loc='lower right')
	plt.title("Z3 Solver runtime for varying numbers of constraints, constraints not satisfiable")
	plt.xlabel("Number of constraints")
	plt.ylabel(f"Average runtime of {runs} runs (ms)")
	
	z1 = np.polyfit(xvals, yvalsUnsat, 1)
	p1 = np.poly1d(z1)
	# Equation of the line
	equation = f"y={z1[0]:.2f}x + {z1[1]:.2f}"
	r_squared = r2_score(yvalsUnsat, p1(xvals))
	plt.annotate(f"Unsatisfiable: {equation}\n r^2 = {r_squared:.2f}", xy=(0.05, 0.85),
	 xycoords='axes fraction', fontsize=10)
	
	z2 = np.polyfit(xvals, yvalsSat, 1)
	p2 = np.poly1d(z2)
	# Equation of the line
	equation = f"y={z2[0]:.2f}x + {z2[1]:.2f}"
	r_squared = r2_score(yvalsSat, p2(xvals))
	plt.annotate(f"Satisfiable: {equation}\n r^2 = {r_squared:.2f}", xy=(0.05, 0.75), xycoords='axes fraction', fontsize=10)

	plt.plot(xvals, p1(xvals), 'r')
	plt.plot(xvals, p2(xvals), 'b')

	plt.show()
	
runTestsComparison(200, 3)

#runTests(300, 1, True)