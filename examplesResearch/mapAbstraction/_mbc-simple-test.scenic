param weather = 'ClearNoon'
param map_options = dict(useCache=True,writeCache=True, fill_intersections=False, segmentation_len=-1, ref_points=20, tolerance=0.05)
model scenic.simulators.carla.model

param intersectiontesting = 207
param snapToWaypoint = [0, 1]

param constraints = " \
ONREGIONTYPE : [0, intersection]; \
ONREGIONTYPE : [1, intersection]; \
NOCOLLISION : [0, 1]; \
# CANSEE : [0, 1]; \
# HASBEHIND : [0, 1]; \
DOINGMANEUVER : [0, is_left]; \
DOINGMANEUVER : [1, is_straight]; \
# COLLIDINGPATHSAHEAD : [1, 0]; \
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