# param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

r = 50

ego = Car \
    with color[188/256, 185/256, 183/256] # Silver
a1 = Car in CircularRegion(ego, r), \
    with color [194/256, 92/256, 85/256] # red
a2 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)), \
    with color [75/256, 119/256, 157/256] # blue
a3 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)).intersect(CircularRegion(a2, r)), \
    with color [219/256, 191/256, 105/256] # yellow
a4 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)).intersect(CircularRegion(a2, r)).intersect(CircularRegion(a3, r)), \
    with color [68/256, 160/256, 135/256] # green
a5 = Car in CircularRegion(ego, r).intersect(CircularRegion(a1, r)).intersect(CircularRegion(a2, r)).intersect(CircularRegion(a3, r)).intersect(CircularRegion(a4, r)), \
    with color [197/256, 166/256, 134/256] # brown
