param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [3, 1]; \
HASINFRONT : [3, 1]; \
DISTCLOSE : [3, 1]; \
CANSEE : [2, 0]; \
HASINFRONT : [2, 0]; \
DISTFAR : [2, 0]; \
HASTOLEFT : [2, 1]; \
DISTMED : [2, 1]; \
HASTOLEFT : [3, 0]; \
DISTFAR : [3, 0]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [3, 2]; \
DISTFAR : [3, 2]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]
