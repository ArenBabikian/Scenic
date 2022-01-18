param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [0, 5]; \
HASINFRONT : [0, 5]; \
CANSEE : [1, 6]; \
HASINFRONT : [1, 6]; \
CANSEE : [3, 6]; \
HASINFRONT : [3, 6]; \
CANSEE : [0, 2]; \
HASINFRONT : [0, 2]; \
CANSEE : [4, 6]; \
HASINFRONT : [4, 6]; \
HASBEHIND : [0, 6]; \
CANSEE : [3, 1]; \
HASINFRONT : [3, 1]; \
DISTMED : [3, 1]; \
HASTOLEFT : [3, 2]; \
DISTMED : [3, 2]; \
HASTOLEFT : [4, 2]; \
DISTFAR : [4, 2]; \
HASTOLEFT : [3, 5]; \
HASTOLEFT : [4, 5]; \
HASBEHIND : [1, 5]; \
HASTOLEFT : [0, 4]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [2, 6]; \
HASTORIGHT : [3, 4]; \
HASBEHIND : [5, 6]; \
HASTOLEFT : [4, 1]; \
DISTFAR : [4, 1]; \
HASTOLEFT : [3, 0]; \
DISTMED : [3, 0]; \
HASTOLEFT : [2, 5]; \
"
model scenic.simulators.carla.model

o6 = Car with color[0.1953125, 0.1953125, 0.1953125]
o5 = Car in SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car in SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5)).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 20, o1.heading-(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.265625, 0.625, 0.52734375]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.85546875, 0.74609375, 0.41015625]
