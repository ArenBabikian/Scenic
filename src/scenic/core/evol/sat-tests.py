from scenic.core.evol.constraints import Cstr_type, Cstr
from scenic.core.evol.sat import validate_sat

# sat
# validate_sat([
#     Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
#     Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
# ])

# unsat
# validate_sat([Cstr(Cstr_type.HASINFRONT, 'o1', 'o1')])

# validate_sat([Cstr(Cstr_type.DISTFAR, 'o1', 'o1')])

# validate_sat([
#     Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2')
# ])

# validate_sat([
#     Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2'),
#     Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1')
# ])

# validate_sat([
#     Cstr(Cstr_type.DISTMED, 'o5', 'o6'),
#     Cstr(Cstr_type.DISTFAR, 'o6', 'o5')
# ])
