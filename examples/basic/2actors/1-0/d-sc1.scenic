param map = localPath('/usr/src/app/maps/town02.xodr')
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car left of o1 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]

