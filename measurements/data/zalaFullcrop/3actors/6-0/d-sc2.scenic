param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 0]; \
HASTORIGHT : [2, 1]; \
HASINFRONT : [0, 1]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2))), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o2
require o2 can see ego
require 10 <= (distance from o2 to ego) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
