# pip install .
# pip install z3-solver
# python src/scenic/core/evol/sat-experiments.py

import re
from scenic.core.evol.constraints import Cstr_type, Cstr

from z3 import *

from sat import *

# Add a global implication rule, for all objects, one constraint => not(other constraints)
def validateWithGlobalImplications(constraints):
    solver = Solver()
    o1 = Const('__dummyObject1__', SceneObject)
    o2 = Const('__dummyObject2__', SceneObject)

    for f in constraintClasses['positional']:
        others = constraintClasses['positional'].difference({f})
        for g in others:
            solver.add(ForAll([o1, o2], Implies(f(o1, o2), Not(g(o1, o2)))))
    
    for f in constraintClasses['distance']:
        others = constraintClasses['distance'].difference({f})
        for g in others:
            solver.add(ForAll([o1, o2], Implies(f(o1, o2), Not(g(o1, o2)))))

    for constraint in constraints:
        solver.add(convertToZ3Constraint(constraint))
    result = solver.check()
    print(str(result) + '\n')

def validateWithCounts(constraints):
    solver = Solver()
    o1 = Const('__dummyObject1__', SceneObject)
    o2 = Const('__dummyObject2__', SceneObject)
    posFns = [left(o1, o2), right(o1, o2), front(o1, o2), behind(o1, o2)]
    distFns = [close(o1, o2), med(o1, o2), far(o1, o2)]
    metaconstraints = [
        #Each constraint in a set precludes the others
        ForAll([o1, o2], Sum([If(posFns[i], 1, 0) for i in range(len(posFns))]) <= 1),
        ForAll([o1, o2], Sum([If(distFns[i], 1, 0) for i in range(len(distFns))]) <= 1)
    ]
    # satisfied constraints
    z3Constraints = list(filter(lambda x: x is not None, map(convertToZ3Constraint, constraints)))
    solver.add(metaconstraints)
    solver.add(z3Constraints)
    result = solver.check()
    print(str(result) + '\n')

# For each predicate, add negations of predicates that must not hold
def validateWithIndividualNegations(constraints):
    solver = Solver()
    for constraint in constraints:
        f = constraintMap[constraint.type]
        src = Const(constraint.src, SceneObject)
        tgt = Const(constraint.tgt, SceneObject)
        solver.add(f(src, tgt))
        if f in constraintClasses['positional'] or f in constraintClasses['distance']:
            for g in next(filter(lambda c: f in c, constraintClasses.values())).difference({f}):
                solver.add(Not(g(src, tgt)))
    result = solver.check()
    print(str(result) + '\n')

alternatives = [validateWithGlobalImplications, validateWithCounts, validateWithIndividualNegations]

validateWithGlobalImplications([
    Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
    Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
])

validateWithGlobalImplications([
    Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
    Cstr(Cstr_type.DISTMED, 'o5', 'o6'),
    Cstr(Cstr_type.DISTFAR, 'o5', 'o6')
])

def convertLineToScenicConstraint(s):
    elements = re.search('([A-Z]*) : \[(.*), (.*)\]', s)
    return Cstr(Cstr_type[elements.group(1)], f'object{elements.group(2)}', f'object{elements.group(3)}')
def convertInputToScenicConstraints(s):
    return map(convertLineToScenicConstraint, filter(lambda s: re.search('([A-Z]*) : \[(.*), (.*)\]', s), s.split('; ')))

bigExample_sat = """HASTOLEFT : [2, 4]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [3, 2]; \
HASTOLEFT : [4, 5]; \
HASTOLEFT : [4, 6]; \
HASTORIGHT : [1, 3]; \
HASTORIGHT : [1, 4]; \
HASTORIGHT : [2, 1]; \
HASTORIGHT : [3, 4]; \
HASTORIGHT : [4, 0]; \
HASBEHIND : [1, 6]; \
HASBEHIND : [2, 0]; \
HASBEHIND : [3, 5]; \
HASBEHIND : [3, 6]; \
HASBEHIND : [6, 0]; \
HASBEHIND : [6, 1]; \
HASBEHIND : [6, 2]; \
HASBEHIND : [6, 3]; \
HASINFRONT : [0, 2]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [0, 5]; \
HASINFRONT : [0, 6]; \
HASINFRONT : [2, 6]; \
HASINFRONT : [3, 0]; \
HASINFRONT : [4, 1]; \
HASINFRONT : [5, 0]; \
HASINFRONT : [5, 2]; \
HASINFRONT : [5, 3]; \
HASINFRONT : [5, 4]; \
DISTCLOSE : [3, 2]; \
DISTCLOSE : [4, 3]; \
DISTMED : [1, 0]; \
DISTMED : [2, 1]; \
DISTMED : [3, 0]; \
DISTMED : [3, 1]; \
DISTMED : [4, 0]; \
DISTMED : [4, 1]; \
DISTMED : [4, 2]; \
DISTMED : [5, 2]; \
DISTMED : [5, 3]; \
DISTMED : [6, 5]; \
DISTFAR : [2, 0]; \
DISTFAR : [5, 0]; \
DISTFAR : [5, 1]; \
DISTFAR : [5, 4]; \
DISTFAR : [6, 0]; \
DISTFAR : [6, 1]; \
DISTFAR : [6, 2]; \
DISTFAR : [6, 3]; \
DISTFAR : [6, 4]; \
"""

bigExample_unsat = bigExample_sat + "DISTCLOSE : [6, 4]"

for f in alternatives:
    f(convertInputToScenicConstraints(bigExample_sat))
    f(convertInputToScenicConstraints(bigExample_unsat))