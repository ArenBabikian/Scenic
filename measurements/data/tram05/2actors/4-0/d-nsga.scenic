param map = localPath('/usr/src/app/maps/tram05.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
NOCOLLISION : [0, 1]; \
CANSEE : [0, 1]; \
HASBEHIND : [1, 0]; \
HASINFRONT : [0, 1]; \
DISTFAR : [1, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
