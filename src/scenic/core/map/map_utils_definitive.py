

from scenic.core.regions import EmptyRegion
from scenic.core.vectors import Vector

####################
# COLLISION
####################

def find_colliding_region(reg1, reg2):
    """Rerturns the collision region, if any and a possible heuristic value"""
    SIZETHRESHOLD = 2*4.5 # size of a car

    try:
        collision_reg = reg1.intersect(reg2)
    except:
        return EmptyRegion(''), 1
    
    # CASE 1: one of the regions if None
    if isinstance(collision_reg, EmptyRegion):
        return collision_reg, 1
    
    # CASE 2: overlap is a line
    aabb = collision_reg.getAABB()
    aabbArea = (aabb[0][1] - aabb[0][0]) * (aabb[1][1] - aabb[1][0])

    if aabbArea < SIZETHRESHOLD:
        # print('Adjacent)')
        return EmptyRegion(''), 1
    
    return collision_reg, 0


def is_collision_ahead(actor, collisionRegion):
    lane = actor.currentLane
    cl = lane.centerline

    # Actor position (projected to cl, in case ~snapToWaypoint)
    pos = cl.project(actor.position)
    posVec = Vector(pos.x, pos.y)

    # Start of centerline
    # print(cl.lineString)
    clstart = cl.points[0]
    clStartVec = Vector(clstart[0], clstart[1])
    # print(type(posVec))

    # start of centerline in collision region
    clInCollision = cl.intersect(collisionRegion) # TODO might do an optimizatin by checking through points for first point in the region
    clstartcoll = clInCollision.points[0]
    clStartCollVec = Vector(clstartcoll[0], clstartcoll[1])

    # This is a  straight-line approximation for now, asusming convex function
    d_pos = clStartVec.distanceTo(posVec) 
    d_coll = clStartVec.distanceTo(clStartCollVec)
    # print(d_pos)
    # print(d_coll)
    # print('...')
    # return True
    if d_pos <= d_coll:
        return True
    else:
        return False
    