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
CANSEE : [1, 4]; \
CANSEE : [1, 6]; \
CANSEE : [3, 2]; \
CANSEE : [4, 1]; \
CANSEE : [4, 2]; \
CANSEE : [4, 3]; \
CANSEE : [4, 5]; \
CANSEE : [5, 2]; \
CANSEE : [5, 3]; \
CANSEE : [6, 1]; \
CANSEE : [6, 2]; \
CANSEE : [6, 3]; \
CANSEE : [6, 4]; \
CANSEE : [6, 5]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [0, 4]; \
HASTOLEFT : [0, 5]; \
HASTOLEFT : [0, 6]; \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [4, 0]; \
HASTOLEFT : [5, 0]; \
HASTOLEFT : [5, 1]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [6, 0]; \
HASTORIGHT : [1, 0]; \
HASTORIGHT : [3, 5]; \
HASBEHIND : [2, 4]; \
HASBEHIND : [2, 5]; \
HASBEHIND : [2, 6]; \
HASBEHIND : [3, 4]; \
HASBEHIND : [3, 6]; \
HASBEHIND : [4, 6]; \
HASBEHIND : [5, 4]; \
HASBEHIND : [5, 6]; \
HASINFRONT : [4, 2]; \
HASINFRONT : [4, 3]; \
HASINFRONT : [4, 5]; \
HASINFRONT : [5, 2]; \
HASINFRONT : [6, 2]; \
HASINFRONT : [6, 3]; \
HASINFRONT : [6, 4]; \
HASINFRONT : [6, 5]; \
DISTCLOSE : [5, 3]; \
DISTCLOSE : [6, 4]; \
DISTMED : [3, 1]; \
DISTMED : [3, 2]; \
DISTMED : [4, 1]; \
DISTMED : [5, 1]; \
DISTMED : [5, 2]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 0]; \
DISTFAR : [4, 0]; \
DISTFAR : [4, 2]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 0]; \
DISTFAR : [5, 4]; \
DISTFAR : [6, 0]; \
DISTFAR : [6, 1]; \
DISTFAR : [6, 2]; \
DISTFAR : [6, 3]; \
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
