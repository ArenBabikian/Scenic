param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [0, 2]; \
HASINFRONT : [0, 2]; \
HASTOLEFT : [0, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in CircularRegion(o2, 50).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)), with color[0.734375, 0.72265625, 0.71484375]
