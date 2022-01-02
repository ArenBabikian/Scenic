param map = localPath('/usr/src/app/maps/tram05.xodr')
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in CircularRegion(o2, 20).difference(CircularRegion(o2, 10)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(CircularRegion(o1, 10)).intersect(CircularRegion(o2, 20)).difference(CircularRegion(o2, 10)), with color[0.734375, 0.72265625, 0.71484375]
