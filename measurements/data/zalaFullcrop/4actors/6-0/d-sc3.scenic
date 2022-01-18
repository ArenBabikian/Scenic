param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [3, 2]; \
HASINFRONT : [3, 2]; \
DISTMED : [3, 2]; \
CANSEE : [3, 1]; \
HASINFRONT : [3, 1]; \
DISTFAR : [3, 1]; \
CANSEE : [2, 1]; \
HASINFRONT : [2, 1]; \
DISTCLOSE : [2, 1]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [3, 0]; \
DISTFAR : [3, 0]; \
HASTOLEFT : [2, 0]; \
DISTMED : [2, 0]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]
