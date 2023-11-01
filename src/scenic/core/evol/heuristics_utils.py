
#  DISTANCE-BASED Utils

def dist_closest_corner_to_container(actor, container):
    maxDist = 0
    for corner in actor.corners:
        dist = container.distanceTo(corner)
        if dist > maxDist:
            maxDist = dist
    return maxDist

def dist_center_to_container(actor, container):
    return container.distanceTo(actor.position)