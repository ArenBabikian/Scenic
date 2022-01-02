param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 1]; \
HASTORIGHT : [2, 0]; \
HASBEHIND : [0, 3]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o3 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]

require o1 can see o2
require o2 can see ego
require o2 can see o1
require o2 can see o3
require o3 can see ego
require (distance from o3 to ego) <= 10 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
