param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]

require o1 can see ego
require (distance from o1 to ego) <= 10 
