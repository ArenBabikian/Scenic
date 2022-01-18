param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 5]; \
HASINFRONT : [1, 5]; \
HASBEHIND : [0, 5]; \
CANSEE : [1, 2]; \
HASINFRONT : [1, 2]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [0, 3]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [1, 3]; \
HASTOLEFT : [2, 5]; \
HASBEHIND : [4, 5]; \
DISTMED : [4, 3]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [4, 2]; \
DISTMED : [4, 2]; \
HASTORIGHT : [3, 5]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o3 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5)).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car in SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.265625, 0.625, 0.52734375]
o1 = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o2, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o4, 50, o4.heading, math.radians(22.5)).intersect(SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o5, 50)).difference(CircularRegion(o5, 20)), with color[0.734375, 0.72265625, 0.71484375]
