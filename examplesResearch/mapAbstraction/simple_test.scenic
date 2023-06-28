param weather = 'ClearNoon'
model scenic.simulators.carla.model

param constraints = " ONREGIONTYPE : [0, road]; \
ONREGIONTYPE : [1, road]; \
ONREGIONTYPE : [2, road]; \
COLLIDESATMANEUVER : [0, is_right]; \
"

ego = Car with color[0.7578125, 0.359375, 0.33203125]
oRight = Car with color[0.734375, 0.72265625, 0.71484375]
oFront = Car with color[0.734375, 0.72265625, 0.71484375]