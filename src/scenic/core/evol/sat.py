from scenic.core.evol.constraints import Cstr_type

from z3 import *

# set_param(proof = True)

def validate_sat(constraints):
    # All objects in the constraints
    objectNames = set(['-1']) # Let -1 always exist, to make unary rules valid
    regionTypeNames = ['default', # Default region wrt. actor type
        'drivable', # All lanes union all intersections.
        'walkable', # All sidewalks union all crossings.
        'road', # All roads (not part of an intersection).
        'lane', # All lanes
        'intersection', # All intersections.
        'crossing', # All pedestrian crossings.
        'sidewalk', # All sidewalks
        'curb', # All curbs of ordinary roads.
        'shoulder']
    for constraint in constraints:
        objectNames.add(str(constraint.src))
        #if constraint.type == Cstr_type.ONREGIONTYPE:
            #regionTypeNames.add(str(constraint.tgt))
        #else:
        if constraint.type != Cstr_type.ONREGIONTYPE and constraint.type != Cstr_type.ONROAD:
            objectNames.add(str(constraint.tgt))

    objectNames = list(objectNames)
    #regionTypeNames = list(regionTypeNames)
    
    SceneObject, objectRefs = EnumSort('SceneObject', objectNames)
    RegionType, regionTypeRefs = EnumSort('RegionType', regionTypeNames)

    # Look up the object literal ref (internal representation in z3) by name
    objectRefsDict = dict(zip(objectNames, objectRefs))
    regionTypeRefsDict = dict(zip(regionTypeNames, regionTypeRefs))

    Bool = BoolSort()

    onRoad = Function('onRoad', SceneObject, SceneObject, Bool)
    onRegionType = Function('onRegionType', SceneObject, RegionType, Bool)

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
        Cstr_type.ONREGIONTYPE: onRegionType,
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
    # TODO: Region type
    subtype = Function('isSubtypeOf', RegionType, RegionType, Bool)

    solver.add(isSubtypeOf(regionTypeRefsDict['lane'], regionTypeRefsDict['road']))
    solver.add(isSubtypeOf(regionTypeRefsDict['lane'], regionTypeRefsDict['drivable']))
    solver.add(isSubtypeOf(regionTypeRefsDict['road'], regionTypeRefsDict['drivable']))
    solver.add(isSubtypeOf(regionTypeRefsDict['intersection'], regionTypeRefsDict['drivable']))
    solver.add(isSubtypeOf(regionTypeRefsDict['sidewalk'], regionTypeRefsDict['walkable']))
    solver.add(isSubtypeOf(regionTypeRefsDict['crossing'], regionTypeRefsDict['walkable']))

    solver.add(ForAll(x, subtype(x, x)))


    # Loop
    for constraintClass in { 'positional', 'distance' }: # TODO: Add vis and coll
        constraintFunctions = constraintFunctionsInClass[constraintClass]
        for f in constraintFunctions:
            solver.add(ForAll([o1, o2], Implies(f(o1, o2), o1 != o2)))
    
    # Symmetry
    for constraintClass in { 'distance' }: # TODO: Add noColl
        constraintFunctions = constraintFunctionsInClass[constraintClass]
        for f in constraintFunctions:
            solver.add(ForAll([o1, o2], Implies(f(o1, o2), f(o2, o1))))

    # "Uniqueness"
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
    return str(result) == 'sat'
