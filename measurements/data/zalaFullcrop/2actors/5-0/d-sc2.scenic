param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [1, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car in SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5)), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see ego
require 10 <= (distance from o1 to ego) <= 20 
