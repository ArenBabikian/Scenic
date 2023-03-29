param constraints = "ONREGIONTYPE : [0, 3]; \
                   ONREGIONTYPE : [1, 3]; \
                   ONREGIONTYPE : [2, 5]; \
                   ONREGIONTYPE : [3, 7]; \
                   CANSEE : [0, 1]; \
                   CANSEE : [0, 2]; \
                   CANSEE : [0, 3]; \
                   HASINFRONT : [0, 2]; \
                   HASTORIGHT : [0, 3]; \
                   NOCOLLISION : [0, 1]; \
                   NOCOLLISION : [0, 2]; \
                   NOCOLLISION : [0, 3]; \
                   NOCOLLISION : [1, 2]; \
                   NOCOLLISION : [1, 3]; \
                   NOCOLLISION : [2, 3];"
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
Pedestrian
Pedestrian
Pedestrian