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
CANSEE : [0, 3]; \
CANSEE : [0, 5]; \
CANSEE : [0, 6]; \
CANSEE : [1, 3]; \
CANSEE : [1, 6]; \
CANSEE : [2, 1]; \
CANSEE : [2, 3]; \
CANSEE : [2, 5]; \
CANSEE : [2, 6]; \
CANSEE : [3, 5]; \
CANSEE : [3, 6]; \
CANSEE : [4, 0]; \
CANSEE : [4, 1]; \
CANSEE : [4, 2]; \
CANSEE : [4, 3]; \
CANSEE : [4, 5]; \
CANSEE : [4, 6]; \
CANSEE : [5, 3]; \
CANSEE : [5, 6]; \
CANSEE : [6, 0]; \
CANSEE : [6, 1]; \
CANSEE : [6, 2]; \
CANSEE : [6, 3]; \
CANSEE : [6, 4]; \
HASTOLEFT : [1, 0]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [5, 0]; \
HASTOLEFT : [5, 1]; \
HASTOLEFT : [5, 2]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [5, 4]; \
HASTOLEFT : [6, 1]; \
HASTOLEFT : [6, 5]; \
HASTORIGHT : [0, 1]; \
HASTORIGHT : [0, 2]; \
HASTORIGHT : [1, 5]; \
HASTORIGHT : [3, 1]; \
HASTORIGHT : [3, 5]; \
HASBEHIND : [3, 0]; \
HASBEHIND : [3, 4]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [0, 6]; \
HASINFRONT : [1, 3]; \
HASINFRONT : [1, 6]; \
HASINFRONT : [2, 1]; \
HASINFRONT : [2, 5]; \
HASINFRONT : [4, 1]; \
HASINFRONT : [4, 3]; \
HASINFRONT : [4, 5]; \
HASINFRONT : [5, 6]; \
DISTCLOSE : [4, 2]; \
DISTMED : [1, 0]; \
DISTMED : [2, 0]; \
DISTMED : [2, 1]; \
DISTMED : [3, 0]; \
DISTMED : [3, 1]; \
DISTMED : [4, 0]; \
DISTMED : [4, 1]; \
DISTFAR : [3, 2]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 0]; \
DISTFAR : [5, 1]; \
DISTFAR : [5, 2]; \
DISTFAR : [5, 3]; \
DISTFAR : [5, 4]; \
DISTFAR : [6, 0]; \
DISTFAR : [6, 1]; \
DISTFAR : [6, 2]; \
DISTFAR : [6, 3]; \
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
