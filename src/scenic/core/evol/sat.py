from scenic.core.evol.constraints import Cstr_type, Cstr

from z3 import *

# set_param(proof = True)

solver = Solver()

SceneObject = DeclareSort('SceneObject')
Bool = BoolSort()

left = Function('left', SceneObject, SceneObject, Bool)
right = Function('right', SceneObject, SceneObject, Bool)
front = Function('front', SceneObject, SceneObject, Bool)
behind = Function('behind', SceneObject, SceneObject, Bool)

close = Function('close', SceneObject, SceneObject, Bool)
med = Function('med', SceneObject, SceneObject, Bool)
far = Function('far', SceneObject, SceneObject, Bool)

o1 = Const('__dummyObject1__', SceneObject)
o2 = Const('__dummyObject2__', SceneObject)

posFns = [left(o1, o2), right(o1, o2), front(o1, o2), behind(o1, o2)]
distFns = [close(o1, o2), med(o1, o2), far(o1, o2)]

metaconstraints = [
    #Each constraint in a set precludes the others
    ForAll([o1, o2], Sum([If(posFns[i], 1, 0) for i in range(len(posFns))]) <= 1),
    ForAll([o1, o2], Sum([If(distFns[i], 1, 0) for i in range(len(distFns))]) <= 1)
]

def convertToZ3Constraint(constraint):
    src = Const(constraint.src, SceneObject)
    tgt = Const(constraint.tgt, SceneObject)
    constraintMap = {
            Cstr_type.HASTOLEFT: left(src, tgt),
            Cstr_type.HASTORIGHT: right(src, tgt),
            Cstr_type.HASBEHIND: behind(src, tgt),
            Cstr_type.HASINFRONT: front(src, tgt),
            Cstr_type.DISTCLOSE: close(src, tgt),
            Cstr_type.DISTMED: med(src, tgt),
            Cstr_type.DISTFAR: far(src, tgt)
        }
    return constraintMap.get(constraint.type)

def validate_constraints(constraints):
    # satisfied constraints
    z3Constraints = list(filter(lambda x: x is not None, map(convertToZ3Constraint, constraints)))
    solver.reset()
    solver.add(metaconstraints)
    solver.add(z3Constraints)
    result = solver.check()
    print(str(result) + '\n')


    # if str(result) == 'sat':
    #     print(solver.model()) # Doesn't really matter
    #     for c in z3Constraints:
    #         print(c, solver.model().eval(c)) # Expect all true
    # else:
        # print(solver.proof()) # This is extremely long and not readable

#satisfied
validate_constraints([
    Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
    Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
])

#unsatisfied
validate_constraints([
    Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
    Cstr(Cstr_type.DISTMED, 'o5', 'o6'),
    Cstr(Cstr_type.DISTFAR, 'o5', 'o6')
])
