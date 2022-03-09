param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 6]; \
HASINFRONT : [1, 6]; \
CANSEE : [3, 5]; \
HASTORIGHT : [3, 5]; \
CANSEE : [0, 6]; \
HASINFRONT : [0, 6]; \
CANSEE : [2, 5]; \
HASINFRONT : [2, 5]; \
HASTORIGHT : [1, 5]; \
CANSEE : [0, 5]; \
CANSEE : [3, 6]; \
HASBEHIND : [3, 4]; \
CANSEE : [2, 6]; \
CANSEE : [0, 3]; \
HASINFRONT : [0, 3]; \
CANSEE : [1, 3]; \
HASINFRONT : [1, 3]; \
CANSEE : [4, 5]; \
HASINFRONT : [4, 5]; \
HASTORIGHT : [0, 2]; \
HASTOLEFT : [6, 5]; \
DISTFAR : [6, 5]; \
HASTORIGHT : [0, 1]; \
CANSEE : [6, 4]; \
DISTFAR : [6, 4]; \
DISTFAR : [3, 2]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.265625, 0.625, 0.52734375]
o6 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))), with color[0.1953125, 0.1953125, 0.1953125]
o2 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o2, 50, o2.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.radians(22.5))).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 20, o6.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o6, 50, o6.heading, math.radians(22.5))).intersect(SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.734375, 0.72265625, 0.71484375]
