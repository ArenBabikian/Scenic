param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [0, 2]; \
HASINFRONT : [0, 2]; \
HASBEHIND : [1, 2]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)), with color[0.734375, 0.72265625, 0.71484375]
