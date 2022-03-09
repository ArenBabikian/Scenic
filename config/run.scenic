# param map = localPath('../maps/CARLA/Town02.xodr')
param constraints = "ONROAD : [0, -1]; \
                   ONROAD : [1, -1]; \
                   ONROAD : [2, -1]; \
                   ONROAD : [3, -1]; \
                   NOCOLLISION : [0, 1]; \
                   NOCOLLISION : [0, 2]; \
                   NOCOLLISION : [1, 2]; \
                   NOCOLLISION : [0, 3]; \
                   NOCOLLISION : [1, 3]; \
                   NOCOLLISION : [2, 3]; \
                   CANSEE : [0, 1]; \
                   HASTOLEFT : [1, 2]; \
                  HASINFRONT : [2, 3]; \
                   DISTFAR : [1, 3];"
model scenic.simulators.carla.model

# o0 is ego

ego = Car \
    with color[188/256, 185/256, 183/256] # Silver
a = Car \
    with color [194/256, 92/256, 85/256] # red
b = Car \
    with color [75/256, 119/256, 157/256] # blue
c = Car \
    with color [68/256, 160/256, 135/256] # green
d = Car \
    with color [75/256, 119/256, 157/256] # blue
e = Car \
    with color [68/256, 160/256, 135/256] # green

