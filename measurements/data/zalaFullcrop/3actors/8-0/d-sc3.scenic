param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [0, 2]; \
CANSEE : [0, 1]; \
CANSEE : [1, 2]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o2, 50, o2.heading, math.radians(22.5))).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)), with color[0.734375, 0.72265625, 0.71484375]
