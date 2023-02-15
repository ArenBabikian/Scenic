model scenic.simulators.carla.model

param constraints = " DISTCLOSE : [0, 1]; \
                   HASINFRONT : [0, 1]; \
                   HASINFRONT : [1, 2]; \
                   DISTCLOSE : [1, 2]; \
                   HASINFRONT : [0, 3]; \
                   CANSEEBLOCK : [0, 3]; \
                   DISTFAR : [0, 3]; "
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
a = Car with color [194/256, 92/256, 85/256] # red
b = Car with color [75/256, 119/256, 157/256] # blue
c = Car with color [68/256, 160/256, 135/256] # green