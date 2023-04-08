model scenic.simulators.carla.model

param constraints = "ONROAD : [0, -1]; \
                   ONROAD : [1, -1]; \
                   ONROAD : [2, -1]; \
                   DISTCLOSE : [0, 1]; \
                   HASINFRONT : [0, 1]; \
                   HIDDEN : [0, 2]; \
                   DISTFAR : [0, 2]; "
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
a = Car with color [194/256, 92/256, 85/256] # red
b = Car with color [75/256, 119/256, 157/256] # blue