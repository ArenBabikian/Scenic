param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 2]; \
HASINFRONT : [1, 2]; \
CANSEE : [1, 0]; \
DISTCLOSE : [1, 0]; \
HASBEHIND : [2, 0]; \
DISTFAR : [2, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
