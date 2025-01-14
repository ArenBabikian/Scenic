

from scenic.core.regions import EmptyRegion
from scenic.core.vectors import Vector

####################
# COLLISION
####################

def find_colliding_region(reg1, reg2, handle_centerlines=False):
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
    areaOverapprox = (aabb[0][1] - aabb[0][0]) * (aabb[1][1] - aabb[1][0])
    areaOverapprox = sum(collision_reg.cumulativeTriangleAreas) # better area approximation

    if areaOverapprox < SIZETHRESHOLD:
        # print('Adjacent)')
        return EmptyRegion(''), 1
    
    if handle_centerlines:
        cl1 = reg1.centerline
        cl2 = reg2.centerline
        cl1_collision = cl1.intersect(collision_reg)
        cl2_collision = cl2.intersect(collision_reg)
        if isinstance(cl1_collision, EmptyRegion) and isinstance(cl2_collision, EmptyRegion):
            return collision_reg, 1
    
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
    