param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 1]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading-(math.pi/2), math.atan(2.5/2)).intersect(CircularRegion(o1, 50)).difference(CircularRegion(o1, 20)), with color[0.734375, 0.72265625, 0.71484375]
