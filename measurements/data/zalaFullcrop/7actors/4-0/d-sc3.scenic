param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [4, 2]; \
HASTORIGHT : [4, 2]; \
DISTFAR : [4, 2]; \
CANSEE : [4, 3]; \
HASINFRONT : [4, 3]; \
DISTMED : [4, 3]; \
CANSEE : [5, 2]; \
HASTORIGHT : [5, 2]; \
DISTFAR : [5, 2]; \
HASTOLEFT : [1, 6]; \
HASTORIGHT : [0, 6]; \
CANSEE : [5, 3]; \
HASINFRONT : [5, 3]; \
DISTFAR : [5, 3]; \
HASTORIGHT : [4, 6]; \
HASTOLEFT : [0, 2]; \
HASBEHIND : [1, 2]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [1, 5]; \
HASTORIGHT : [4, 5]; \
CANSEE : [6, 3]; \
HASINFRONT : [6, 3]; \
DISTFAR : [6, 3]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [0, 1]; \
CANSEE : [6, 2]; \
DISTFAR : [6, 2]; \
HASBEHIND : [3, 2]; \
DISTFAR : [3, 2]; \
HASTOLEFT : [4, 1]; \
DISTMED : [4, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)), with color[0.85546875, 0.74609375, 0.41015625]
o6 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))), with color[0.1953125, 0.1953125, 0.1953125]
o5 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o6, 10)), with color[0.76953125, 0.6484375, 0.5234375]
o1 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading, math.atan(2/5))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading, math.atan(2/5))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.265625, 0.625, 0.52734375]
ego = Car in SectorRegion(o6, 50, o6.heading, math.radians(22.5)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 20, o6.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.734375, 0.72265625, 0.71484375]
