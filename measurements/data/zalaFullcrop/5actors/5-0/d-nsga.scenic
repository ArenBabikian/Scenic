param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
ONROAD : [3, -1]; \
ONROAD : [4, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [0, 3]; \
NOCOLLISION : [0, 4]; \
NOCOLLISION : [1, 2]; \
NOCOLLISION : [1, 3]; \
NOCOLLISION : [1, 4]; \
NOCOLLISION : [2, 3]; \
NOCOLLISION : [2, 4]; \
NOCOLLISION : [3, 4]; \
CANSEE : [0, 2]; \
CANSEE : [0, 3]; \
CANSEE : [3, 2]; \
CANSEE : [4, 0]; \
CANSEE : [4, 2]; \
CANSEE : [4, 3]; \
HASTORIGHT : [0, 1]; \
HASTORIGHT : [1, 0]; \
HASTORIGHT : [1, 3]; \
HASTORIGHT : [1, 4]; \
HASTORIGHT : [2, 1]; \
HASTORIGHT : [3, 1]; \
HASTORIGHT : [4, 1]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [2, 0]; \
HASBEHIND : [2, 3]; \
HASBEHIND : [2, 4]; \
HASBEHIND : [3, 0]; \
HASBEHIND : [3, 4]; \
HASINFRONT : [0, 2]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [3, 2]; \
HASINFRONT : [4, 0]; \
HASINFRONT : [4, 2]; \
HASINFRONT : [4, 3]; \
DISTCLOSE : [3, 0]; \
DISTMED : [4, 0]; \
DISTMED : [4, 3]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 1]; \
DISTFAR : [3, 2]; \
DISTFAR : [4, 1]; \
DISTFAR : [4, 2]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car with color[0.265625, 0.625, 0.52734375]
