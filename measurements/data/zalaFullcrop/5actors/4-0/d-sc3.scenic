param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [0, 4]; \
HASINFRONT : [0, 4]; \
CANSEE : [1, 4]; \
HASTORIGHT : [1, 4]; \
CANSEE : [0, 3]; \
HASINFRONT : [0, 3]; \
HASTOLEFT : [1, 3]; \
HASBEHIND : [2, 3]; \
HASBEHIND : [1, 0]; \
DISTFAR : [1, 0]; \
HASTOLEFT : [3, 4]; \
HASTOLEFT : [2, 0]; \
DISTMED : [2, 0]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o3 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.radians(22.5))).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 50, ego.heading, math.atan(2/5))).intersect(CircularRegion(o4, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
