param weather = 'ClearNoon'
param map_options = dict(useCache=False, writeCache=False, fill_intersections=False, segmentation_len=3, ref_points=20, tolerance=0.05)
model scenic.simulators.carla.model

param constraints = " ONREGIONTYPE : [0, road]; \
ONREGIONTYPE : [1, road]; \
NOTONSAMEROAD : [0, 1]; \
DISTFAR : [0, 1]; \
COLLIDESATMANEUVER : [0, is_right]; \
"

ego = Car with color[0.7578125, 0.359375, 0.33203125]
oRight = Car with color[0.734375, 0.72265625, 0.71484375]
