param constraints = "ONROAD : [0, -1]; \
                   ONROAD : [1, -1]; \
                   NOCOLLISION : [0, 1]; \
                   HASINFRONT : [0, 1]; \
                   DISTFAR : [0, 1];"
model scenic.simulators.carla.model

ego = Pedestrian with color[188/256, 185/256, 183/256] # Silver
a = Pedestrian with color [194/256, 92/256, 85/256] # red

