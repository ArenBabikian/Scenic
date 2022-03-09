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
CANSEE : [1, 0]; \
CANSEE : [1, 4]; \
CANSEE : [1, 5]; \
CANSEE : [2, 0]; \
CANSEE : [2, 1]; \
CANSEE : [2, 3]; \
CANSEE : [2, 4]; \
CANSEE : [2, 5]; \
CANSEE : [3, 0]; \
CANSEE : [3, 1]; \
CANSEE : [3, 4]; \
CANSEE : [3, 5]; \
CANSEE : [4, 0]; \
CANSEE : [5, 1]; \
CANSEE : [5, 2]; \
CANSEE : [5, 3]; \
HASTOLEFT : [0, 5]; \
HASTOLEFT : [4, 5]; \
HASTOLEFT : [5, 0]; \
HASTOLEFT : [5, 4]; \
HASBEHIND : [0, 1]; \
HASBEHIND : [0, 2]; \
HASBEHIND : [0, 3]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [1, 2]; \
HASBEHIND : [3, 2]; \
HASBEHIND : [4, 1]; \
HASBEHIND : [4, 2]; \
HASBEHIND : [4, 3]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [1, 4]; \
HASINFRONT : [2, 0]; \
HASINFRONT : [2, 1]; \
HASINFRONT : [2, 3]; \
HASINFRONT : [2, 4]; \
HASINFRONT : [2, 5]; \
HASINFRONT : [3, 0]; \
HASINFRONT : [3, 4]; \
HASINFRONT : [3, 5]; \
HASINFRONT : [4, 0]; \
HASINFRONT : [5, 2]; \
HASINFRONT : [5, 3]; \
DISTCLOSE : [4, 1]; \
DISTMED : [3, 1]; \
DISTMED : [3, 2]; \
DISTMED : [4, 0]; \
DISTMED : [5, 0]; \
DISTMED : [5, 4]; \
DISTFAR : [1, 0]; \
DISTFAR : [2, 0]; \
DISTFAR : [2, 1]; \
DISTFAR : [3, 0]; \
DISTFAR : [4, 2]; \
DISTFAR : [4, 3]; \
DISTFAR : [5, 1]; \
DISTFAR : [5, 2]; \
DISTFAR : [5, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car with color[0.265625, 0.625, 0.52734375]
o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
