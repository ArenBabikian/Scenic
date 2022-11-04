param constraints = "ONROAD : [0, -1]; \
                   ONSIDEWALK : [1, -1]; \
                   ONROAD : [2, -1]; \
                   ONROAD : [3, -1]; \
                   ONSIDEWALK : [4, -1]; \
                   NOCOLLISION : [0, 1]; \
                   NOCOLLISION : [0, 2]; \
                   NOCOLLISION : [1, 2]; \
                   CANSEE : [0, 3]; \
                   HASTOLEFT : [3, 4]; \
                   HASINFRONT : [1, 2];"
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
a = Car with color [194/256, 92/256, 85/256] # red
b = Car with color [75/256, 119/256, 157/256] # blue

Pedestrian
Pedestrian