param map = localPath('/usr/src/app/maps/town02.xodr')
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car in SectorRegion(ego, 50, ego.heading, math.atan(2/5)), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o1
require 10 <= (distance from o1 to ego) <= 20 
