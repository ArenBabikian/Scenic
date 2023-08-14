param weather = 'ClearNoon'
param map_options = dict(useCache=True,writeCache=True, fill_intersections=False, segmentation_len=8, ref_points=20, tolerance=0.05)
model scenic.simulators.carla.model

param intersectiontesting = 1574

param constraints = " \
ONREGIONTYPE : [0, intersection]; \
ONREGIONTYPE : [1, intersection]; \
ONREGIONTYPE : [2, intersection]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [0, 2]; \
NOCOLLISION : [1, 2]; \
CANSEE : [0, 1]; \
CANSEE : [0, 2]; \
HASTORIGHT : [2, 1]; \
#HASINFRONT : [2, 0]; \
DOINGMANEUVER : [0, is_left]; \
# DOINGMANEUVER : [1, is_right]; \
DOINGMANEUVER : [2, is_straight]; \
"

#HASINFRONT : [0, 1]; \
#HASINFRONT : [0, 2]; \
#HASTORIGHT : [1, 0]; \
#HASINFRONT : [2, 0]; \

#DISTMED : [0, 2]; \
#DISTMED : [1, 2]; \
#DISTCLOSE : [0, 1]; \

ego = Car with color[0.7578125, 0.359375, 0.33203125]
oRight = Car with color[0.734375, 0.72265625, 0.71484375]
oFront = Car with color[0.734375, 0.72265625, 0.71484375]