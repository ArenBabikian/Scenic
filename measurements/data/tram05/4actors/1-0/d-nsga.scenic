param map = localPath('/usr/src/app/maps/tram05.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
ONROAD : [3, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [0, 3]; \
NOCOLLISION : [1, 2]; \
NOCOLLISION : [1, 3]; \
NOCOLLISION : [2, 3]; \
CANSEE : [0, 2]; \
CANSEE : [0, 3]; \
CANSEE : [1, 0]; \
CANSEE : [1, 2]; \
CANSEE : [1, 3]; \
CANSEE : [2, 0]; \
CANSEE : [2, 1]; \
HASTOLEFT : [2, 3]; \
HASTORIGHT : [0, 3]; \
HASTORIGHT : [3, 0]; \
HASTORIGHT : [3, 1]; \
HASTORIGHT : [3, 2]; \
HASBEHIND : [0, 1]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [1, 2]; \
HASINFRONT : [2, 1]; \
DISTCLOSE : [1, 0]; \
DISTCLOSE : [2, 0]; \
DISTMED : [2, 1]; \
DISTMED : [3, 2]; \
DISTFAR : [3, 0]; \
DISTFAR : [3, 1]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
