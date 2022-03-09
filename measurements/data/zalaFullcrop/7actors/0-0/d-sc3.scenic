param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [6, 4]; \
HASINFRONT : [6, 4]; \
DISTCLOSE : [6, 4]; \
CANSEE : [6, 5]; \
HASINFRONT : [6, 5]; \
DISTFAR : [6, 5]; \
HASBEHIND : [5, 4]; \
DISTFAR : [5, 4]; \
CANSEE : [6, 3]; \
HASINFRONT : [6, 3]; \
DISTFAR : [6, 3]; \
CANSEE : [5, 3]; \
HASTOLEFT : [5, 3]; \
DISTCLOSE : [5, 3]; \
HASTOLEFT : [0, 4]; \
HASBEHIND : [2, 4]; \
CANSEE : [1, 4]; \
HASTOLEFT : [0, 3]; \
CANSEE : [6, 2]; \
HASINFRONT : [6, 2]; \
DISTFAR : [6, 2]; \
HASTOLEFT : [0, 5]; \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [0, 2]; \
HASTORIGHT : [1, 0]; \
DISTFAR : [1, 0]; \
HASTOLEFT : [6, 0]; \
DISTFAR : [6, 0]; \
CANSEE : [5, 2]; \
HASINFRONT : [5, 2]; \
DISTMED : [5, 2]; \
HASBEHIND : [3, 4]; \
CANSEE : [6, 1]; \
DISTFAR : [6, 1]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o3 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(o4, 50, o4.heading, math.radians(22.5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o5 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
o6 = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))), with color[0.1953125, 0.1953125, 0.1953125]
