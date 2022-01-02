param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [2, 1]; \
HASINFRONT : [2, 1]; \
DISTMED : [2, 1]; \
CANSEE : [0, 3]; \
HASTORIGHT : [0, 3]; \
HASBEHIND : [0, 1]; \
HASTOLEFT : [2, 3]; \
CANSEE : [2, 0]; \
DISTCLOSE : [2, 0]; \
CANSEE : [1, 3]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))).intersect(CircularRegion(o1, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o1, 50, o1.heading, math.radians(22.5))).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)), with color[0.29296875, 0.46484375, 0.61328125]
