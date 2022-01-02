param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [2, 0]; \
HASINFRONT : [2, 0]; \
DISTMED : [2, 0]; \
HASBEHIND : [1, 0]; \
DISTMED : [1, 0]; \
HASTORIGHT : [1, 3]; \
HASTOLEFT : [2, 3]; \
CANSEE : [3, 0]; \
DISTMED : [3, 0]; \
HASTOLEFT : [1, 2]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)), with color[0.7578125, 0.359375, 0.33203125]
