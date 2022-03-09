param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
ONROAD : [3, -1]; \
ONROAD : [4, -1]; \
ONROAD : [5, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [0, 3]; \
NOCOLLISION : [0, 4]; \
NOCOLLISION : [0, 5]; \
NOCOLLISION : [1, 2]; \
NOCOLLISION : [1, 3]; \
NOCOLLISION : [1, 4]; \
NOCOLLISION : [1, 5]; \
NOCOLLISION : [2, 3]; \
NOCOLLISION : [2, 4]; \
NOCOLLISION : [2, 5]; \
NOCOLLISION : [3, 4]; \
NOCOLLISION : [3, 5]; \
NOCOLLISION : [4, 5]; \
CANSEE : [0, 1]; \
CANSEE : [1, 0]; \
CANSEE : [1, 2]; \
CANSEE : [1, 3]; \
CANSEE : [1, 5]; \
CANSEE : [2, 3]; \
CANSEE : [4, 0]; \
CANSEE : [4, 1]; \
CANSEE : [4, 2]; \
CANSEE : [4, 3]; \
CANSEE : [5, 0]; \
CANSEE : [5, 1]; \
CANSEE : [5, 4]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [2, 3]; \
HASTOLEFT : [2, 4]; \
HASTOLEFT : [2, 5]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [3, 4]; \
HASTOLEFT : [3, 5]; \
HASTOLEFT : [4, 5]; \
HASTOLEFT : [5, 0]; \
HASTOLEFT : [5, 2]; \
HASTOLEFT : [5, 3]; \
HASTORIGHT : [0, 4]; \
HASTORIGHT : [0, 5]; \
HASTORIGHT : [3, 2]; \
HASTORIGHT : [4, 1]; \
HASBEHIND : [2, 1]; \
HASBEHIND : [3, 1]; \
HASINFRONT : [1, 2]; \
HASINFRONT : [1, 3]; \
DISTCLOSE : [3, 0]; \
DISTCLOSE : [3, 2]; \
DISTCLOSE : [5, 0]; \
DISTMED : [2, 0]; \
DISTMED : [4, 0]; \
DISTMED : [5, 2]; \
DISTMED : [5, 3]; \
DISTMED : [5, 4]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 1]; \
DISTFAR : [4, 1]; \
DISTFAR : [4, 2]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 1]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car with color[0.265625, 0.625, 0.52734375]
o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
