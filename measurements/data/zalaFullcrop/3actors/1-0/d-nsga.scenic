param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [1, 2]; \
CANSEE : [2, 1]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [1, 2]; \
HASINFRONT : [2, 1]; \
DISTMED : [2, 0]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 1]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
