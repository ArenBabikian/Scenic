param constraints = " \ONREGIONTYPE : [0, 1]; \
                    ONREGIONTYPE : [1, 7]; \
                    NOCOLLISION : [0, 1]; \
                    CANSEE : [1, 0]; \
                    HASTORIGHT : [0, 1]; \
                    DISTMED : [1, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]

Pedestrian