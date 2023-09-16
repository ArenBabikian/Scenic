# param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

param snapToWaypoint = [0, 1]

param constraints = " \
ONREGIONTYPE : [0, intersection]; \
ONREGIONTYPE : [1, intersection]; \
NOCOLLISION : [0, 1]; \
DOINGMANEUVER : [0, is_right]; \
COLLIDINGPATHSAHEAD : [0, 1]; \
"

ego = Car with color[0.7578125, 0.359375, 0.33203125]
oRight = Car with color[0.734375, 0.72265625, 0.71484375]