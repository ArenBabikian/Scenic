param map = localPath('C:/git/Scenic/maps/tram05.xodr')
param weather = 'ClearNoon'
model scenic.simulators.carla.model

param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [1, 2]; \
CANSEE : [0, 1]; \
HASTORIGHT : [0, 1]; \
HASTOLEFT : [1, 0]; \
HASINFRONT : [0, 2]; \
HASBEHIND : [2, 0]; \
DISTMED : [0, 2]; \
DISTMED : [1, 2]; \
DISTCLOSE : [0, 1]; \
"

ego = Car with color[0.7578125, 0.359375, 0.33203125]
oRight = Car with color[0.734375, 0.72265625, 0.71484375]
oFront = Car with color[0.734375, 0.72265625, 0.71484375]