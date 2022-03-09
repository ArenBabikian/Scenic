param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 2]; \
HASINFRONT : [3, 2]; \
HASTOLEFT : [0, 1]; \
HASTORIGHT : [3, 0]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2))), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]

require o1 can see o2
require o3 can see ego
require o3 can see o1
require o3 can see o2
require (distance from o1 to ego) <= 10 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o3 to o2) <= 20 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
