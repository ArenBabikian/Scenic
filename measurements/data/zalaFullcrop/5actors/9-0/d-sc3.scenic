param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
CANSEE : [1, 3]; \
HASINFRONT : [1, 3]; \
CANSEE : [4, 3]; \
HASINFRONT : [4, 3]; \
DISTFAR : [4, 3]; \
HASBEHIND : [0, 3]; \
HASTOLEFT : [2, 1]; \
DISTFAR : [2, 1]; \
HASTOLEFT : [2, 3]; \
CANSEE : [4, 1]; \
HASINFRONT : [4, 1]; \
DISTFAR : [4, 1]; \
HASBEHIND : [0, 1]; \
HASTOLEFT : [2, 4]; \
HASBEHIND : [2, 0]; \
DISTFAR : [2, 0]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5)).intersect(CircularRegion(o3, 20)).difference(CircularRegion(o3, 10)), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car in SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5)).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))), with color[0.265625, 0.625, 0.52734375]
ego = Car in SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5)).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o4, 20)).difference(CircularRegion(o4, 10)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(CircularRegion(o3, 50)).difference(CircularRegion(o3, 20)).intersect(CircularRegion(o4, 50)).difference(CircularRegion(o4, 20)), with color[0.29296875, 0.46484375, 0.61328125]
