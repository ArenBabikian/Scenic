param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 5]; \
HASINFRONT : [1, 5]; \
CANSEE : [1, 0]; \
HASTORIGHT : [1, 0]; \
DISTCLOSE : [1, 0]; \
CANSEE : [1, 2]; \
HASINFRONT : [1, 2]; \
HASBEHIND : [3, 2]; \
DISTFAR : [3, 2]; \
CANSEE : [0, 4]; \
HASTOLEFT : [0, 4]; \
CANSEE : [5, 2]; \
HASTOLEFT : [5, 2]; \
DISTCLOSE : [5, 2]; \
CANSEE : [1, 4]; \
HASTOLEFT : [3, 0]; \
DISTMED : [3, 0]; \
HASBEHIND : [3, 5]; \
HASBEHIND : [3, 4]; \
HASTORIGHT : [5, 4]; \
DISTMED : [5, 4]; \
CANSEE : [0, 2]; \
HASTOLEFT : [1, 3]; \
CANSEE : [0, 5]; \
DISTMED : [4, 2]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car in SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2)), with color[0.265625, 0.625, 0.52734375]
o5 = Car in SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 50, o4.heading+math.pi, math.atan(2/5))), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o3, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.7578125, 0.359375, 0.33203125]
