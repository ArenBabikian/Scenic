param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [2, 1]; \
HASINFRONT : [2, 1]; \
DISTFAR : [2, 1]; \
CANSEE : [2, 0]; \
HASINFRONT : [2, 0]; \
DISTMED : [2, 0]; \
HASBEHIND : [0, 1]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))).intersect(CircularRegion(o1, 10)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o1, 50, o1.heading, math.radians(22.5))).intersect(SectorRegion(ego, 50, ego.heading, math.atan(2/5))).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]
