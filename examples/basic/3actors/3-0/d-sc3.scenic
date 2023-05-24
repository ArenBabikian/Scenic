param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 0]; \
HASINFRONT : [1, 0]; \
DISTMED : [1, 0]; \
HASBEHIND : [2, 0]; \
DISTFAR : [2, 0]; \
HASTOLEFT : [1, 2]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(ego, 50, ego.heading, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 50, ego.heading, math.atan(2/5))).intersect(CircularRegion(o2, 10)), with color[0.7578125, 0.359375, 0.33203125]
