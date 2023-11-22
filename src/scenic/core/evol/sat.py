from scenic.core.evol.constraints import Cstr_type, Cstr

from z3 import *

# set_param(proof = True)

def validate_sat(constraints):
    # All objects in the constraints
    objectNames = set()
    for constraint in constraints:
        objectNames.add(str(constraint.src))
        if constraint.type != Cstr_type.ONREGIONTYPE:
            objectNames.add(str(constraint.tgt))
    objectNames = list(objectNames)
    
    SceneObject, objectRefs = EnumSort('SceneObject', objectNames)

    # Look up the object literal ref (internal representation in z3) by name
    objectRefsDict = dict(zip(objectNames, objectRefs))

    Bool = BoolSort()

    onRoad = Function('onRoad', SceneObject, SceneObject, Bool)

    left = Function('left', SceneObject, SceneObject, Bool)
    right = Function('right', SceneObject, SceneObject, Bool)
    front = Function('front', SceneObject, SceneObject, Bool)
    behind = Function('behind', SceneObject, SceneObject, Bool)

    close = Function('close', SceneObject, SceneObject, Bool)
    med = Function('med', SceneObject, SceneObject, Bool)
    far = Function('far', SceneObject, SceneObject, Bool)

    constraintFunctionsInClass = {
        'positional': { left, right, front, behind },
        'distance': { close, med, far }
    }

    constraintMap = {
        Cstr_type.ONROAD: onRoad,
        Cstr_type.HASTOLEFT: left,
        Cstr_type.HASTORIGHT: right,
        Cstr_type.HASBEHIND: behind,
        Cstr_type.HASINFRONT: front,
        Cstr_type.DISTCLOSE: close,
        Cstr_type.DISTMED: med,
        Cstr_type.DISTFAR: far
    }

    def convertToZ3Constraint(constraint):
        src = objectRefsDict[str(constraint.src)]
        tgt = objectRefsDict[str(constraint.tgt)]
        return constraintMap.get(constraint.type)(src, tgt)

    solver = Solver()

    o1 = Const('__dummyObject1__', SceneObject)
    o2 = Const('__dummyObject2__', SceneObject)

    solver.add(ForAll([o1, o2], Implies(onRoad(o1, o2), o2 == objectRefsDict['-1'])))

    for constraintClass in { 'positional', 'distance' }:
        constraintFunctions = constraintFunctionsInClass[constraintClass]
        for f in constraintFunctions:
            others = constraintFunctions.difference({f})
            for g in others:
                solver.add(ForAll([o1, o2], Implies(f(o1, o2), Not(g(o1, o2)))))

    for constraint in constraints:
        if constraint.type in constraintMap.keys(): # TODO: remove after we finish all constraints
            solver.add(convertToZ3Constraint(constraint))

    result = solver.check()
    print(str(result) + '\n')
    # if str(result) == 'sat':
        # print(solver.model())
    return str(result) == 'sat'

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
