param constraints = "ONREGIONTYPE : [0, 6]; \
                   ONREGIONTYPE : [1, 1]; \
                   NOCOLLISION : [0, 1];"
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
# a = Car with color [194/256, 92/256, 85/256] # red

Pedestrian