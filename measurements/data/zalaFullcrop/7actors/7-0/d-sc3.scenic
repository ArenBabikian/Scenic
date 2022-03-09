param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 6]; \
HASTOLEFT : [1, 6]; \
CANSEE : [1, 5]; \
HASTOLEFT : [1, 5]; \
CANSEE : [2, 0]; \
HASTOLEFT : [2, 0]; \
DISTFAR : [2, 0]; \
CANSEE : [1, 4]; \
HASINFRONT : [1, 4]; \
CANSEE : [2, 3]; \
HASTOLEFT : [2, 3]; \
CANSEE : [2, 4]; \
HASINFRONT : [2, 4]; \
CANSEE : [1, 0]; \
DISTFAR : [1, 0]; \
CANSEE : [3, 6]; \
HASINFRONT : [3, 6]; \
CANSEE : [3, 5]; \
HASINFRONT : [3, 5]; \
HASTOLEFT : [2, 5]; \
HASTOLEFT : [2, 6]; \
HASTORIGHT : [3, 0]; \
DISTCLOSE : [3, 0]; \
HASTOLEFT : [3, 4]; \
CANSEE : [5, 6]; \
HASTOLEFT : [5, 6]; \
HASTOLEFT : [5, 4]; \
DISTMED : [5, 4]; \
HASTOLEFT : [6, 4]; \
DISTMED : [6, 4]; \
CANSEE : [1, 3]; \
HASTOLEFT : [0, 4]; \
CANSEE : [0, 6]; \
HASTORIGHT : [1, 2]; \
CANSEE : [0, 5]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o6 = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)), with color[0.1953125, 0.1953125, 0.1953125]
o5 = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o6, 20, o6.heading-(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o6, 10)), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 20)).difference(CircularRegion(o6, 10)), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 20)).difference(CircularRegion(o6, 10)), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 20, o6.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 50, o4.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 20)).difference(CircularRegion(o6, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 20, o6.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 50, o4.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 20)).difference(CircularRegion(o6, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)), with color[0.7578125, 0.359375, 0.33203125]
