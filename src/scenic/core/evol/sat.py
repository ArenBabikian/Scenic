from scenic.core.evol.constraints import Cstr_type, Cstr

from z3 import *

# set_param(proof = True)

SceneObject = DeclareSort('SceneObject')
Bool = BoolSort()

left = Function('left', SceneObject, SceneObject, Bool)
right = Function('right', SceneObject, SceneObject, Bool)
front = Function('front', SceneObject, SceneObject, Bool)
behind = Function('behind', SceneObject, SceneObject, Bool)

close = Function('close', SceneObject, SceneObject, Bool)
med = Function('med', SceneObject, SceneObject, Bool)
far = Function('far', SceneObject, SceneObject, Bool)

constraintClasses = {
    'positional': { left, right, front, behind },
    'distance': { close, med, far }
}

constraintMap = {
    Cstr_type.HASTOLEFT: left,
    Cstr_type.HASTORIGHT: right,
    Cstr_type.HASBEHIND: behind,
    Cstr_type.HASINFRONT: front,
    Cstr_type.DISTCLOSE: close,
    Cstr_type.DISTMED: med,
    Cstr_type.DISTFAR: far
}

def convertToZ3Constraint(constraint):
    src = Const(constraint.src, SceneObject)
    tgt = Const(constraint.tgt, SceneObject)
    return constraintMap.get(constraint.type)(src, tgt)

def validate_constraints(constraints):
    solver = Solver()
    for constraint in constraints:
        f = constraintMap[constraint.type]
        src = Const(constraint.src, SceneObject)
        tgt = Const(constraint.tgt, SceneObject)
        if f in constraintClasses['positional'] or f in constraintClasses['distance']:
            solver.add(f(src, tgt))
            for g in next(filter(lambda c: f in c, constraintClasses.values())).difference({f}):
                solver.add(Not(g(src, tgt)))
    result = solver.check()
    print(str(result) + '\n')

    # if str(result) == 'sat':
    #     print(solver.model()) # Doesn't really matter
    #     for c in z3Constraints:
    #         print(c, solver.model().eval(c)) # Expect all true
    # else:
    #     print(solver.proof()) # This is extremely long and not readable

#satisfied
# validate_constraints([
#     Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
#     Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
# ])

#unsatisfied
# validate_constraints([
#     Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
#     Cstr(Cstr_type.DISTMED, 'o5', 'o6'),
#     Cstr(Cstr_type.DISTFAR, 'o5', 'o6')
# ])
