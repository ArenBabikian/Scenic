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
CANSEE : [1, 2]; \
CANSEE : [1, 3]; \
CANSEE : [1, 4]; \
CANSEE : [3, 0]; \
CANSEE : [3, 1]; \
CANSEE : [3, 4]; \
CANSEE : [4, 2]; \
CANSEE : [4, 3]; \
HASTOLEFT : [1, 0]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [2, 3]; \
HASTOLEFT : [3, 2]; \
HASTOLEFT : [4, 0]; \
HASTORIGHT : [0, 1]; \
HASTORIGHT : [0, 4]; \
HASTORIGHT : [4, 1]; \
HASBEHIND : [2, 1]; \
HASBEHIND : [2, 4]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [1, 2]; \
HASINFRONT : [3, 0]; \
HASINFRONT : [4, 2]; \
DISTCLOSE : [4, 0]; \
DISTCLOSE : [4, 1]; \
DISTMED : [1, 0]; \
DISTMED : [3, 2]; \
DISTFAR : [2, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 0]; \
DISTFAR : [3, 1]; \
DISTFAR : [4, 2]; \
DISTFAR : [4, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car with color[0.265625, 0.625, 0.52734375]
