param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 5]; \
HASTOLEFT : [1, 5]; \
CANSEE : [4, 3]; \
HASINFRONT : [4, 3]; \
DISTFAR : [4, 3]; \
HASBEHIND : [2, 5]; \
HASBEHIND : [0, 3]; \
CANSEE : [4, 5]; \
HASTOLEFT : [1, 3]; \
HASBEHIND : [2, 1]; \
DISTFAR : [2, 1]; \
CANSEE : [0, 4]; \
HASTOLEFT : [0, 1]; \
HASTORIGHT : [2, 4]; \
HASTOLEFT : [1, 4]; \
HASTORIGHT : [2, 0]; \
DISTMED : [2, 0]; \
HASTORIGHT : [5, 3]; \
DISTFAR : [5, 3]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car in SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2)), with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.265625, 0.625, 0.52734375]
o1 = Car in SectorRegion(o5, 50, o5.heading, math.radians(22.5)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o4, 10)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.29296875, 0.46484375, 0.61328125]
