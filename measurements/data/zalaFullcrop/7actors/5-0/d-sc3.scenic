param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [2, 1]; \
HASTORIGHT : [2, 1]; \
DISTCLOSE : [2, 1]; \
CANSEE : [3, 6]; \
HASTORIGHT : [3, 6]; \
HASBEHIND : [4, 1]; \
DISTFAR : [4, 1]; \
CANSEE : [2, 5]; \
HASTORIGHT : [2, 5]; \
HASBEHIND : [6, 5]; \
DISTFAR : [6, 5]; \
HASTOLEFT : [4, 3]; \
DISTFAR : [4, 3]; \
HASBEHIND : [4, 2]; \
DISTFAR : [4, 2]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [3, 5]; \
HASTORIGHT : [0, 6]; \
HASTOLEFT : [4, 6]; \
DISTFAR : [3, 1]; \
HASTOLEFT : [2, 6]; \
HASBEHIND : [4, 0]; \
DISTFAR : [4, 0]; \
CANSEE : [1, 5]; \
DISTFAR : [3, 2]; \
DISTFAR : [3, 0]; \
DISTFAR : [6, 1]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o1 = Car in SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o5, 10)), with color[0.7578125, 0.359375, 0.33203125]
o6 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))), with color[0.1953125, 0.1953125, 0.1953125]
o2 = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o6, 20, o6.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 20, o6.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o6, 10)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o2, 50, o2.heading, math.radians(22.5))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.265625, 0.625, 0.52734375]
