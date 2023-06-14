model scenic.simulators.carla.model

# o0 is ego
# This file is meant to see how well scenic scales when placing a certain number of vehicles with simple contraints 
l = 50

ego = Car \
    with color[188/256, 185/256, 183/256] # Silver
a = Car in SectorRegion(ego, l, ego.heading, math.radians(22.5)), \
    with color [194/256, 92/256, 85/256] # red
b = Car in SectorRegion(ego, l, ego.heading, math.radians(22.5)), \
    with color [75/256, 119/256, 157/256] # blue
c = Car in SectorRegion(ego, l, ego.heading, math.radians(22.5)), \
    with color [68/256, 160/256, 135/256] # green
d = Car in SectorRegion(ego, l, ego.heading, math.radians(22.5)), \
    with color [75/256, 119/256, 157/256] # blue
#e = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)), \
#    with color [68/256, 160/256, 135/256] # green
#f = Car in SectorRegion(ego, l, ego.heading, math.radians(22.5)), \
#    with color [75/256, 119/256, 157/256] # blue
#g = Car in SectorRegion(ego, 50, ego.heading, math.radians(22.5)), \
#    with color [68/256, 160/256, 135/256] # green

