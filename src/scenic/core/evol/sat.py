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


o1 = Const('__dummyObject1__', SceneObject)
o2 = Const('__dummyObject2__', SceneObject)
metaconstraints = [
    ForAll([o1, o2], Implies(left(o1, o2), Not(right(o1, o2)))),
    ForAll([o1, o2], Implies(right(o1, o2), Not(left(o1, o2)))),
    ForAll([o1, o2], Implies(front(o1, o2), Not(behind(o1,o2))),
    ForAll([o1, o2], Implies(behind(o1, o2), Not(front(o1,o2)))
]
solver.add(metaconstraints)

def convertToZ3Constraint(constraint):
    src = Const(constraint.src, SceneObject)
    tgt = Const(constraint.tgt, SceneObject)
    if constraint.type == Cstr_type.HASTOLEFT:
        return left(src, tgt)
    if constraint.type == Cstr_type.HASTORIGHT:
        return right(src, tgt)
    if constraint.type == Cstr_type.HASBEHIND:
        return behind(src, tgt)
    if constraint.type == Cstr_type.HASINFRONT:
        return front(src,tgt)

def validate_constraints(constraints):
    z3Constraints = list(map(convertToZ3Constraint, constraints))
    solver.add(z3Constraints)
    result = solver.check()
    print(result)
    # if str(result) == 'sat':
    #     print(solver.model()) # Doesn't really matter
    #     for c in z3Constraints:
    #         print(c, solver.model().eval(c)) # Expect all true
    # else:
        # print(solver.proof()) # This is extremely long and not readable

validate_constraints([
    Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
    Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
    Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
    # Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2'), # conflict
])
