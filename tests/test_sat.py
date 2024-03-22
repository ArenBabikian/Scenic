# pytest test_sat.py

from scenic.core.evol.constraints import Cstr_type, Cstr
from scenic.core.evol.sat import validate_sat
import re

# unsat
def test_self_loop_hasInFront():
    assert not validate_sat([Cstr(Cstr_type.HASINFRONT, 'o1', 'o1')])

def test_self_loop_hasBehind():
    assert not validate_sat([Cstr(Cstr_type.HASBEHIND, 'o1', 'o1')])

def test_self_loop_hasToLeft():
    assert not validate_sat([Cstr(Cstr_type.HASTOLEFT, 'o1', 'o1')])

def test_self_loop_hasToRight():
    assert not validate_sat([Cstr(Cstr_type.HASTORIGHT, 'o1', 'o1')])

def test_self_loop_distFar():
    assert not validate_sat([Cstr(Cstr_type.DISTFAR, 'o1', 'o1')])

def test_self_loop_distMed():
    assert not validate_sat([Cstr(Cstr_type.DISTMED, 'o1', 'o1')])

def test_self_loop_distClose():
    assert not validate_sat([Cstr(Cstr_type.DISTCLOSE, 'o1', 'o1')])

def test_self_loop_canSee():
    assert not validate_sat([Cstr(Cstr_type.CANSEE, 'o1', 'o1')])

def test_self_loop_noCollision():
    assert not validate_sat([Cstr(Cstr_type.NOCOLLISION, 'o1', 'o1')])

def test_position_conflict():
    assert not validate_sat([
        Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
        Cstr(Cstr_type.HASTORIGHT, 'o1', 'o2')
    ])

def test_dist_symmetry_conflict():
    assert not validate_sat([
        Cstr(Cstr_type.DISTMED, 'o5', 'o6'),
        Cstr(Cstr_type.DISTFAR, 'o6', 'o5')
    ])

def test_onregion_conflict():
    assert not validate_sat([
        Cstr(Cstr_type.ONREGIONTYPE, 'o1', 'drivable'),
        Cstr(Cstr_type.ONREGIONTYPE, 'o1', 'curb')
    ])

# sat
def test_position_sat():
    assert validate_sat([
        Cstr(Cstr_type.HASTOLEFT, 'o1', 'o2'),
        Cstr(Cstr_type.HASTOLEFT, 'o2', 'o3'),
        Cstr(Cstr_type.HASTORIGHT, 'o2', 'o1'),
    ])


def test_d_nsga_sat():
    d_nsga_constraints_text = """
    ONROAD : [0, -1]; \
    ONROAD : [1, -1]; \
    ONROAD : [2, -1]; \
    ONROAD : [3, -1]; \
    ONROAD : [4, -1]; \
    ONROAD : [5, -1]; \
    ONROAD : [6, -1]; \
    NOCOLLISION : [0, 1]; \
    NOCOLLISION : [0, 2]; \
    NOCOLLISION : [0, 3]; \
    NOCOLLISION : [0, 4]; \
    NOCOLLISION : [0, 5]; \
    NOCOLLISION : [0, 6]; \
    NOCOLLISION : [1, 2]; \
    NOCOLLISION : [1, 3]; \
    NOCOLLISION : [1, 4]; \
    NOCOLLISION : [1, 5]; \
    NOCOLLISION : [1, 6]; \
    NOCOLLISION : [2, 3]; \
    NOCOLLISION : [2, 4]; \
    NOCOLLISION : [2, 5]; \
    NOCOLLISION : [2, 6]; \
    NOCOLLISION : [3, 4]; \
    NOCOLLISION : [3, 5]; \
    NOCOLLISION : [3, 6]; \
    NOCOLLISION : [4, 5]; \
    NOCOLLISION : [4, 6]; \
    NOCOLLISION : [5, 6]; \
    CANSEE : [1, 2]; \
    CANSEE : [1, 4]; \
    CANSEE : [1, 5]; \
    CANSEE : [2, 1]; \
    CANSEE : [2, 4]; \
    CANSEE : [2, 5]; \
    CANSEE : [3, 6]; \
    HASTOLEFT : [0, 1]; \
    HASTOLEFT : [1, 0]; \
    HASTOLEFT : [1, 2]; \
    HASTOLEFT : [1, 3]; \
    HASTOLEFT : [1, 6]; \
    HASTOLEFT : [2, 3]; \
    HASTOLEFT : [2, 6]; \
    HASTOLEFT : [4, 3]; \
    HASTOLEFT : [4, 6]; \
    HASTOLEFT : [5, 4]; \
    HASTOLEFT : [6, 0]; \
    HASTOLEFT : [6, 3]; \
    HASTORIGHT : [0, 3]; \
    HASTORIGHT : [0, 6]; \
    HASTORIGHT : [2, 1]; \
    HASTORIGHT : [2, 5]; \
    HASTORIGHT : [3, 6]; \
    HASTORIGHT : [5, 0]; \
    HASTORIGHT : [5, 1]; \
    HASTORIGHT : [5, 2]; \
    HASBEHIND : [0, 4]; \
    HASBEHIND : [3, 4]; \
    HASBEHIND : [3, 5]; \
    HASBEHIND : [4, 0]; \
    HASBEHIND : [4, 1]; \
    HASBEHIND : [4, 2]; \
    HASBEHIND : [5, 3]; \
    HASBEHIND : [5, 6]; \
    HASBEHIND : [6, 4]; \
    HASBEHIND : [6, 5]; \
    HASINFRONT : [1, 4]; \
    HASINFRONT : [2, 4]; \
    DISTCLOSE : [1, 0]; \
    DISTCLOSE : [2, 0]; \
    DISTCLOSE : [2, 1]; \
    DISTCLOSE : [5, 1]; \
    DISTCLOSE : [5, 2]; \
    DISTCLOSE : [6, 3]; \
    DISTMED : [5, 0]; \
    DISTFAR : [3, 0]; \
    DISTFAR : [3, 1]; \
    DISTFAR : [3, 2]; \
    DISTFAR : [4, 0]; \
    DISTFAR : [4, 1]; \
    DISTFAR : [4, 2]; \
    DISTFAR : [4, 3]; \
    DISTFAR : [5, 3]; \
    DISTFAR : [5, 4]; \
    DISTFAR : [6, 0]; \
    DISTFAR : [6, 1]; \
    DISTFAR : [6, 2]; \
    DISTFAR : [6, 4]; \
    DISTFAR : [6, 5]; \
    """
    assert validate_sat(convertInputToScenicConstraints(d_nsga_constraints_text))

def convertLineToScenicConstraint(s):
    elements = re.search('([A-Z]*) : \[(.*), (.*)\]', s)
    return Cstr(Cstr_type[elements.group(1)], f'object{elements.group(2)}', f'object{elements.group(3)}')
def convertInputToScenicConstraints(s):
    return map(convertLineToScenicConstraint, filter(lambda s: re.search('([A-Z]*) : \[(.*), (.*)\]', s), s.split('; ')))
