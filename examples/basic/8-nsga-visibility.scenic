param constraints = "CANSEE : [0, 1]; \
                    ONREGIONTYPE : [0, 1]; \
                    ONREGIONTYPE : [1, 1]; \
                    NOCOLLISION : [0, 1];"
model scenic.simulators.carla.model

ego = Car with color [188/256, 185/256, 183/256] # Silver
a = Car with color [68/256, 160/256, 135/256] # green