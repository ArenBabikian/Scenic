# param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

r = 30

ego = Car \
    with color[188/256, 185/256, 183/256] # Silver
a1 = Car in CircularRegion(ego, r), \
    with color [194/256, 92/256, 85/256] # red