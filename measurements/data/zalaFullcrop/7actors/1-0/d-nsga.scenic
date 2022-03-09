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
CANSEE : [0, 6]; \
CANSEE : [1, 0]; \
CANSEE : [1, 2]; \
CANSEE : [1, 6]; \
CANSEE : [2, 1]; \
CANSEE : [2, 4]; \
CANSEE : [2, 5]; \
CANSEE : [3, 1]; \
CANSEE : [3, 2]; \
CANSEE : [3, 4]; \
CANSEE : [3, 5]; \
CANSEE : [5, 4]; \
CANSEE : [6, 0]; \
CANSEE : [6, 1]; \
CANSEE : [6, 2]; \
CANSEE : [6, 3]; \
CANSEE : [6, 4]; \
CANSEE : [6, 5]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [2, 3]; \
HASTOLEFT : [4, 1]; \
HASTOLEFT : [4, 3]; \
HASTOLEFT : [5, 1]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [5, 4]; \
HASTORIGHT : [1, 3]; \
HASTORIGHT : [3, 0]; \
HASTORIGHT : [3, 6]; \
HASTORIGHT : [4, 5]; \
HASBEHIND : [0, 1]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [2, 6]; \
HASBEHIND : [4, 0]; \
HASBEHIND : [4, 2]; \
HASBEHIND : [4, 6]; \
HASBEHIND : [5, 6]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [1, 6]; \
HASINFRONT : [2, 4]; \
HASINFRONT : [3, 1]; \
HASINFRONT : [3, 4]; \
HASINFRONT : [3, 5]; \
HASINFRONT : [6, 1]; \
HASINFRONT : [6, 2]; \
HASINFRONT : [6, 4]; \
HASINFRONT : [6, 5]; \
DISTCLOSE : [5, 4]; \
DISTMED : [2, 0]; \
DISTMED : [3, 1]; \
DISTMED : [4, 1]; \
DISTMED : [4, 2]; \
DISTMED : [5, 1]; \
DISTMED : [5, 2]; \
DISTMED : [6, 0]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 0]; \
DISTFAR : [3, 2]; \
DISTFAR : [4, 0]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 0]; \
DISTFAR : [5, 3]; \
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
