param constraints = "ONREGIONTYPE : [0, 5]; \
                   ONREGIONTYPE : [1, 3]; \
                   ONREGIONTYPE : [2, 7]; \
                   HASINFRONT : [0, 1]; \
                   DISTCLOSE : [0, 1]; \
                   HASTOLEFT : [0, 2]; \
                   DISTCLOSE : [0, 2]; \
                   NOCOLLISION : [0, 1]; \
                   NOCOLLISION : [1, 2]"
model scenic.simulators.carla.model

ego = Car with color [188/256, 185/256, 183/256] # Silver
a = Car with color [68/256, 160/256, 135/256] # green
Pedestrian