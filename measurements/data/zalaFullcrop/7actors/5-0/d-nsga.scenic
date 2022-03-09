param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
ONROAD : [3, -1]; \
ONROAD : [4, -1]; \
ONROAD : [5, -1]; \
ONROAD : [6, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [0, 3]; \
NOCOLLISION : [0, 4]; \
NOCOLLISION : [0, 5]; \
NOCOLLISION : [0, 6]; \
NOCOLLISION : [1, 2]; \
NOCOLLISION : [1, 3]; \
NOCOLLISION : [1, 4]; \
NOCOLLISION : [1, 5]; \
NOCOLLISION : [1, 6]; \
NOCOLLISION : [2, 3]; \
NOCOLLISION : [2, 4]; \
NOCOLLISION : [2, 5]; \
NOCOLLISION : [2, 6]; \
NOCOLLISION : [3, 4]; \
NOCOLLISION : [3, 5]; \
NOCOLLISION : [3, 6]; \
NOCOLLISION : [4, 5]; \
NOCOLLISION : [4, 6]; \
NOCOLLISION : [5, 6]; \
CANSEE : [1, 2]; \
CANSEE : [1, 4]; \
CANSEE : [1, 5]; \
CANSEE : [2, 1]; \
CANSEE : [2, 4]; \
CANSEE : [2, 5]; \
CANSEE : [3, 6]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [1, 0]; \
HASTOLEFT : [1, 2]; \
HASTOLEFT : [1, 3]; \
HASTOLEFT : [1, 6]; \
HASTOLEFT : [2, 3]; \
HASTOLEFT : [2, 6]; \
HASTOLEFT : [4, 3]; \
HASTOLEFT : [4, 6]; \
HASTOLEFT : [5, 4]; \
HASTOLEFT : [6, 0]; \
HASTOLEFT : [6, 3]; \
HASTORIGHT : [0, 3]; \
HASTORIGHT : [0, 6]; \
HASTORIGHT : [2, 1]; \
HASTORIGHT : [2, 5]; \
HASTORIGHT : [3, 6]; \
HASTORIGHT : [5, 0]; \
HASTORIGHT : [5, 1]; \
HASTORIGHT : [5, 2]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [3, 4]; \
HASBEHIND : [3, 5]; \
HASBEHIND : [4, 0]; \
HASBEHIND : [4, 1]; \
HASBEHIND : [4, 2]; \
HASBEHIND : [5, 3]; \
HASBEHIND : [5, 6]; \
HASBEHIND : [6, 4]; \
HASBEHIND : [6, 5]; \
HASINFRONT : [1, 4]; \
HASINFRONT : [2, 4]; \
DISTCLOSE : [1, 0]; \
DISTCLOSE : [2, 0]; \
DISTCLOSE : [2, 1]; \
DISTCLOSE : [5, 1]; \
DISTCLOSE : [5, 2]; \
DISTCLOSE : [6, 3]; \
DISTMED : [5, 0]; \
DISTFAR : [3, 0]; \
DISTFAR : [3, 1]; \
DISTFAR : [3, 2]; \
DISTFAR : [4, 0]; \
DISTFAR : [4, 1]; \
DISTFAR : [4, 2]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 3]; \
DISTFAR : [5, 4]; \
DISTFAR : [6, 0]; \
DISTFAR : [6, 1]; \
DISTFAR : [6, 2]; \
DISTFAR : [6, 4]; \
DISTFAR : [6, 5]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car with color[0.265625, 0.625, 0.52734375]
o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o6 = Car with color[0.1953125, 0.1953125, 0.1953125]
