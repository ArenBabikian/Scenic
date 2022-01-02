# param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

r = 30

ego = Car \
    with color[188/256, 185/256, 183/256] # Silver
a1 = Car in CircularRegion(ego, r), \
    with color [194/256, 92/256, 85/256] # red
a2 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)), \
    with color [75/256, 119/256, 157/256] # blue
a3 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)).intersect(CircularRegion(a2, r)), \
    with color [219/256, 191/256, 105/256] # yellow