
from scenic.core.evol.constraints import Cstr_type
from scenic.core.evol.heuristics import name2maneuverType
from scenic.core.evol.sat import validate_sat

def validate_constraints(scenario, constraints):
    maneuver_cons = list(filter(lambda c: c.type == Cstr_type.DOINGMANEUVER, constraints))
    for c in maneuver_cons:
        scenario.actorIdsWithManeuver[c.src] = name2maneuverType(c.tgt)

    if not validate_sat(constraints):
        exit(1)

# TODO add some validation to prevent the DOINGMANEUVER constraint if intersectiontesting parameter is not specified

