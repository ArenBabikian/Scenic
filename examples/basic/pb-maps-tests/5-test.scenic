param constraints = "NOCOLLISION : [0, 1]; \
                    NOCOLLISION : [0, 2]; \
                    NOCOLLISION : [0, 3]; \
                    NOCOLLISION : [0, 4]; \
                    NOCOLLISION : [0, 5]; \
                    NOCOLLISION : [1, 2]; \
                    NOCOLLISION : [1, 3]; \
                    NOCOLLISION : [1, 4]; \
                    NOCOLLISION : [1, 5]; \
                    NOCOLLISION : [2, 3]; \
                    NOCOLLISION : [2, 4]; \
                    NOCOLLISION : [2, 5]; \
                    NOCOLLISION : [3, 4]; \
                    NOCOLLISION : [3, 5]; \
                    NOCOLLISION : [4, 5]; \
                    CANSEE : [0, 1]; \
                    HASINFRONT : [0, 1]; \
                    HASBEHIND : [0, 2]; \
                    DISTCLOSE : [0, 2]; \
                    HASTOLEFT : [3, 4]; \
                    DISTMED : [3, 4]; \
                    HASTORIGHT : [5, 4]; \
                    DISTFAR : [4, 5];"
model scenic.simulators.carla.model

ego = Car with color[188/256, 185/256, 183/256] # Silver
a = Car with color [194/256, 92/256, 85/256] # red
b = Car with color [75/256, 119/256, 157/256] # blue 
c = Car with color [194/256, 92/256, 85/256] # red
d = Car with color [75/256, 119/256, 157/256] # blue 
e = Car with color [68/256, 160/256, 135/256] # green