param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [0, 5]; \
HASINFRONT : [0, 5]; \
CANSEE : [0, 3]; \
HASINFRONT : [0, 3]; \
CANSEE : [0, 6]; \
HASINFRONT : [0, 6]; \
CANSEE : [0, 2]; \
HASINFRONT : [0, 2]; \
CANSEE : [4, 3]; \
DISTCLOSE : [4, 3]; \
CANSEE : [2, 6]; \
HASINFRONT : [2, 6]; \
CANSEE : [4, 1]; \
HASINFRONT : [4, 1]; \
DISTMED : [4, 1]; \
CANSEE : [5, 3]; \
HASINFRONT : [5, 3]; \
DISTMED : [5, 3]; \
HASTOLEFT : [4, 6]; \
CANSEE : [4, 2]; \
DISTMED : [4, 2]; \
HASBEHIND : [1, 6]; \
HASTORIGHT : [1, 3]; \
HASTOLEFT : [4, 5]; \
CANSEE : [0, 1]; \
CANSEE : [2, 5]; \
HASBEHIND : [6, 3]; \
DISTFAR : [6, 3]; \
HASTORIGHT : [4, 0]; \
DISTMED : [4, 0]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o6 = Car in SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5)), with color[0.1953125, 0.1953125, 0.1953125]
o5 = Car in SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o6, 20)).difference(CircularRegion(o6, 10)), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car in SectorRegion(o5, 50, o5.heading, math.radians(22.5)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o3, 10)).intersect(CircularRegion(o5, 20)).difference(CircularRegion(o5, 10)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o5, 50, o5.heading, math.radians(22.5)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o6, 50, o6.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.734375, 0.72265625, 0.71484375]
o4 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(o5, 50, o5.heading, math.radians(22.5))).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 20, o1.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)).intersect(CircularRegion(o6, 50)).difference(CircularRegion(o6, 20)), with color[0.265625, 0.625, 0.52734375]
