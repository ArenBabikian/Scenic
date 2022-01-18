param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 3]; \
HASINFRONT : [1, 3]; \
CANSEE : [2, 3]; \
HASINFRONT : [2, 3]; \
CANSEE : [1, 0]; \
HASINFRONT : [1, 0]; \
DISTMED : [1, 0]; \
HASBEHIND : [2, 0]; \
DISTMED : [2, 0]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [2, 4]; \
CANSEE : [3, 0]; \
HASINFRONT : [3, 0]; \
DISTFAR : [3, 0]; \
CANSEE : [1, 2]; \
HASINFRONT : [1, 2]; \
HASTORIGHT : [3, 4]; \
DISTFAR : [4, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o4 = Car in SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2)), with color[0.265625, 0.625, 0.52734375]
o3 = Car in SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(o3, 50, o3.heading, math.radians(22.5)).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)).intersect(SectorRegion(o3, 50, o3.heading, math.radians(22.5))).intersect(SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(ego, 50, ego.heading, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.7578125, 0.359375, 0.33203125]
