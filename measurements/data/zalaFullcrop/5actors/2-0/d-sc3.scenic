param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [3, 1]; \
HASINFRONT : [3, 1]; \
DISTCLOSE : [3, 1]; \
CANSEE : [4, 1]; \
HASINFRONT : [4, 1]; \
DISTFAR : [4, 1]; \
CANSEE : [3, 2]; \
DISTFAR : [3, 2]; \
CANSEE : [4, 2]; \
DISTMED : [4, 2]; \
HASBEHIND : [0, 2]; \
HASBEHIND : [0, 1]; \
CANSEE : [4, 3]; \
DISTFAR : [4, 3]; \
CANSEE : [4, 0]; \
DISTFAR : [4, 0]; \
HASTORIGHT : [1, 2]; \
DISTCLOSE : [3, 0]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 50)).difference(CircularRegion(o2, 20)), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 20, o1.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))), with color[0.265625, 0.625, 0.52734375]
